from discord.ext import commands

bot = commands.Bot(command_prefix='s!')

bot.load_extension('cogs.snipe')
bot.run('TOKEN')
