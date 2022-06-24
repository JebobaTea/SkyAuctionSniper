import discord
import asyncio
import aiohttp
import re
from discord.ext import commands, tasks

reforges = [" ✦", "⚚ ", " ✪", "✪", "Very Wise ", "Thicc ", "Treacherous ", "Stiff ", "Lucky ", "Jerry's ", "Dirty ",
            "Fabled ", "Suspicious ", "Gilded ", "Warped ", "Withered ", "Bulky ", "Stellar ", "Heated ", "Ambered ",
            "Fruitful ", "Magnetic ", "Fleet ", "Mithraic ", "Auspicious ", "Refined ", "Headstrong ", "Precise ",
            "Spiritual ", "Moil ", "Blessed ", "Toil ", "Bountiful ", "Candied ", "Submerged ", "Reinforced ", "Cubic ",
            "Warped ", "Undead ", "Ridiculous ", "Necrotic ", "Spiked ", "Jaded ", "Loving ", "Perfect ", "Renowned ",
            "Giant ", "Empowered ", "Ancient ", "Sweet ", "Silky ", "Bloody ", "Shaded ", "Gentle ", "Odd ", "Fast ",
            "Fair ", "Epic ", "Sharp ", "Heroic ", "Spicy ", "Legendary ", "Deadly ", "Fine ", "Grand ", "Hasty ",
            "Neat ", "Rapid ", "Unreal ", "Awkward ", "Rich ", "Clean ", "Fierce ", "Heavy ", "Light ", "Mythic ",
            "Pure ", "Smart ", "Titanic ", "Wise ", "Bizarre ", "Itchy ", "Ominous ", "Pleasant ", "Pretty ", "Shiny ",
            "Simple ", "Strange ", "Vivid ", "Godly ", "Demonic ", "Forceful ", "Hurtful ", "Keen ", "Strong ",
            "Superior ", "Unpleasant ", "Zealous "]
auc = []
results = []
prices = {}
cli = aiohttp.client
channel = None
baseURL = 'https://api.hypixel.net/skyblock/auctions?page='


async def request(url):
    async with cli.request('GET', url) as resp:
        return await resp.json()


async def getItem(page=0, first_page=False):
    global prices
    if first_page:
        prices = {}
    resp = await request(baseURL + str(page))
    for auction in resp.get('auctions', []):
        if not "bin" in auction:
            continue
        if "Furniture" in auction['item_lore']:
            continue
        if "Skin" in auction['item_name']:
            continue
        if "Travel Scroll" in auction['item_name']:
            continue
        index = re.sub("\[[^\]]*\] ", "", auction['item_name'])
        index = str(auction['tier']) + " | " + index
        for reforge in reforges:
            if reforge == "Heavy ":
                if "Super Heavy " in index:
                    index = index.replace("Super Heavy ", "")
                else:
                    index = index.replace(reforge, "")
            else:
                index = index.replace(reforge, "")
        if index in prices:
            if prices[index][3] != auction['uuid']:
                if prices[index][0] > auction['starting_bid']:
                    prices[index][1] = prices[index][0]
                    prices[index][0] = auction['starting_bid']
                    prices[index][2] = auction['item_name']
                    prices[index][4] = prices[index][3]
                    prices[index][3] = auction['uuid']
                    prices[index][5] += 1
                elif prices[index][1] > auction['starting_bid'] and prices[index][4] != auction['uuid']:
                    prices[index][1] = auction['starting_bid']
                    prices[index][4] = auction['uuid']
                    prices[index][5] += 1
        else:
            prices[index] = [auction['starting_bid'], float("inf"), auction['item_name'], auction['uuid'], 'UUID', 1]
    return [prices, resp if first_page else {}]


class Snipe(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        global channel
        channel = self.bot.get_channel("CHANNEL")
        self.l.start()

    @tasks.loop(seconds=61.0)
    async def l(self):
        global auc, results, channel
        results = []
        auc, data = await getItem(0, True)
        pages = data.get('totalPages', 0)
        await asyncio.gather(*[getItem(i) for i in range(1, pages)])
        if auc:
            for auction in auc:
                if auc[auction][1] > 500000 and auc[auction][0] / auc[auction][1] < 1 / 10 and auc[auction][1] != float(
                        "inf") and auc[auction][1] < 100000000 and auc[auction][5] > 10:
                    results.append([auc[auction][2], f"{auc[auction][0]:,}", f"{auc[auction][1]:,}",
                                    f"{auc[auction][1] - auc[auction][0]:,}", auction])

            for result in results:
                embed = discord.Embed(color=discord.Color.orange(), title=result[4])
                embed.add_field(name=result[0], value="Being sold for " + str(result[1]) + " at a gap of " + str(
                    result[3]) + " \n Second cheapest: " + str(result[2]), inline=False)
                await channel.send(embed=embed)


def setup(bot):
    bot.add_cog(Snipe(bot))
