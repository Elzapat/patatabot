import os
import discord
from dotenv import load_dotenv
from spongebobcase import tospongebob

def main():
    load_dotenv()
    TOKEN = os.getenv("DISCORD_TOKEN")

    client = discord.Client()

    @client.event
    async def on_ready():
        print(f"{client.user} has connected to Discord!")

    @client.event
    async def on_message(message):
        if message.author == client.user:
            return

        await message.channel.send(tospongebob(message.content))

    client.run(TOKEN)

if __name__ == "__main__":
    main()
