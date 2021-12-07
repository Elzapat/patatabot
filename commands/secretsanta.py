import json
import random

from config import bot

@bot.command(name = "secret-santa", aliases = ["secretsanta", "secret_santa"])
async def secretsanta(ctx, arg = None): #{
    """
    Inscription au secret santa de 2021
    Arguments :
     * aucun argument, permet de s'inscrire
     * "no", permet de se désinscrire
     * "list", permet de lister les participants du Secret Santa
     * "start", permet d'assigner à chaque personne une personne à qui donner un cadeau (envoie le nom en MP)
    """
    SECRET_SANTA_FILE = "secretsanta.json"

    secret_santa_data = {}
    with open(SECRET_SANTA_FILE, "r") as file: #{
        try: #{
            secret_santa_data = json.load(file)
        #}
        except json.decoder.JSONDecodeError: #{
            pass
        #}
    #}

    if "participants" not in secret_santa_data: #{
        secret_santa_data["participants"] = []
    #}

    if arg is None: #{
        if ctx.message.author.id in secret_santa_data["participants"]:
            await ctx.reply(f"{ctx.message.author.mention}, tu es déjà inscrit")
        else:
            secret_santa_data["participants"].append(ctx.message.author.id)
            await ctx.reply(f"{ctx.message.author.mention}, tu as été inscrit")
    #}
    elif arg == "no": #{
        if ctx.message.author.id not in secret_santa_data["participants"]:
            await ctx.reply(f"{ctx.message.author.mention}, tu n'es pas inscrit")
        else:
            secret_santa_data["participants"].remove(ctx.message.author.id)
            await ctx.reply(f"{ctx.message.author.mention}, tu as été desinscrit")
    #}
    elif arg == "list": #{
        guild = ctx.channel.guild

        message = "**Participants du secret santa :**"

        if len(secret_santa_data["participants"]) == 0: #{
            message += "\nPERSONNE"
            await ctx.send(message)
            await ctx.send("<:JeanMarie_Elard:708061398529343529>")
            return
        #}

        for user_id in secret_santa_data["participants"]: #{
            member = await guild.fetch_member(user_id)
            message += f"\n > {member.display_name}"
        #}

        await ctx.send(message)
    #}
    elif arg == "start": #{
        guild = ctx.channel.guild

        og_gifter_id = secret_santa_data["participants"].pop(random.randint(0, len(secret_santa_data["participants"]) - 1))
        gifter_id = og_gifter_id
        giftee_id = og_gifter_id

        while len(secret_santa_data["participants"]) > 0: #{
            giftee_id = secret_santa_data["participants"].pop(random.randint(0, len(secret_santa_data["participants"]) - 1))
            gifter = await bot.fetch_user(gifter_id)
            giftee = await guild.fetch_member(giftee_id)

            await gifter.send(f"La personne à qui tu dois offrir un cadeau est {giftee.display_name}")

            gifter_id = giftee_id
        #}

        gifter = await bot.fetch_user(gifter_id)
        giftee = await guild.fetch_member(og_gifter_id)
        await gifter.send(f"La personne à qui tu dois offrir un cadeau est {giftee.display_name}")
        await ctx.send("Les gens ont été distribués")
    #}

    with open(SECRET_SANTA_FILE, "w") as file: #{
        json.dump(secret_santa_data, file)
    #}
#}
