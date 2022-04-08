import os
from keepalive import keepalive
from discord.ext import commands

bot = commands.Bot(command_prefix="s!")

keepalive()
bot.load_extension("cogs.snipe")
bot.run("TOKEN")
