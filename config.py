import os
import discord
from dotenv import load_dotenv
from discord.ext import commands
from interactions import Client, Intents

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")
GUILD_ID = os.getenv("GUILD_ID")
BASE_URL = os.getenv("BASE_URL")
APERO_MAN_URL = os.getenv("APERO_MAN_URL")
PIXABAY_API_KEY = os.getenv("PIXABAY_API_KEY")
FETEDUJOUR_API_KEY = os.getenv("FETEDUJOUR_API_KEY")
EXIT_DAMES_CODE = os.getenv("EXIT_DAMES_CODE")
intents = discord.Intents.default()
intents.messages = True
intents.guilds = True
intents.reactions = True
intents.message_content = True
bot = commands.Bot(command_prefix = "/", intents=intents)
interactions_bot = Client(token=str(TOKEN), intents=Intents.DEFAULT | Intents.GUILD_MESSAGE_CONTENT)
