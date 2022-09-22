import commands
import asyncio
from config import TOKEN, bot

@bot.event
async def on_ready():
    print(f"{bot.user.display_name} is connected! (Python)")

@bot.event
async def on_message(message):
    # message.content = "/boggle"
    print(message)
    
    await bot.process_commands(message)

def main():
    # loop = asyncio.get_event_loop()
    # task2 = loop.create_task(bot.start(TOKEN, bot=True))
    # task1 = loop.create_task(interactions_bot.start())
    #
    # gathered = asyncio.gather(task1, task2, loop=loop)
    # loop.run_until_complete(gathered)
    _ = bot.run(TOKEN)

if __name__ == "__main__":
    main()
