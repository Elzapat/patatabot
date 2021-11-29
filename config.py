import os
from dotenv import load_dotenv
from discord.ext import commands

load_dotenv()

bot = commands.Bot(command_prefix = "/")
TOKEN = os.getenv("DISCORD_TOKEN")
