import os
from dotenv import load_dotenv
from discord.ext import commands

load_dotenv()

bot = commands.Bot(command_prefix = "/")
TOKEN = os.getenv("DISCORD_TOKEN")
GUILD_ID = os.getenv("GUILD_ID")
BASE_URL = os.getenv("BASE_URL")
APERO_MAN_URL = os.getenv("APERO_MAN_URL")
PIXABAY_API_KEY = os.getenv("PIXABAY_API_KEY")
FETEDUJOUR_API_KEY = os.getenv("FETEDUJOUR_API_KEY")
