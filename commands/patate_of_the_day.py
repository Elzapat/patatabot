import json
import requests
import random

from config import bot, PIXABAY_API_KEY
from discord.ext import tasks

current_patate_of_the_day: str = "https://perdu.com"

@bot.command(name="patate_of_the_day", aliases=["patateOfTheDay", "potd", "patateoftheday", "patate-of-the-day"])
async def patate_of_the_day(ctx):
    await ctx.channel.send(current_patate_of_the_day)

@tasks.loop(hours=24)
async def new_patate_of_the_day_task():
    PIXABAY_API = "https://pixabay.com/api"
    RES_PER_PAGE: int = 10

    response = requests.get(f"{PIXABAY_API}?key={PIXABAY_API_KEY}&lang=fr&q=patate&per_page={RES_PER_PAGE}")

    if response.status_code != requests.codes.ok:
        print(f"Error fetching ze first patates with status code {response.status_code}: ")
        # print(response.json())
        return

    response = response.json()
    total_pages = response["totalHits"] // RES_PER_PAGE

    page = random.randint(1, total_pages)

    response = requests.get(f"{PIXABAY_API}?key={PIXABAY_API_KEY}&lang=fr&q=patate&per_page={RES_PER_PAGE}&page={page}")

    if response.status_code != requests.codes.ok:
        print(f"Error fetching ze random patates with status code {response.status_code}: ")
        # print(response.json())
        return

    response = response.json()

    random_patate_idx = random.randrange(len(response["hits"]))

    global current_patate_of_the_day
    current_patate_of_the_day = response["hits"][random_patate_idx]["largeImageURL"]

new_patate_of_the_day_task.start()
