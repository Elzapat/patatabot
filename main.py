import config
import commands

from config import TOKEN, bot

@bot.event
async def on_ready():
    print(f"{bot.user} has connected to Discord!")

@bot.event
async def on_message(message):
    await bot.process_commands(message)

def main():
    bot.run(TOKEN)

if __name__ == "__main__":
    main()
