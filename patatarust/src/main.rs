mod puissance4;

use puissance4::{check_command_validity, get_leaderbaord, reaction_added, setup_game, Puissance4GameData};
use serenity::{
    async_trait,
    model::{
        application::{
            command::{Command, CommandOptionType},
            interaction::{Interaction, InteractionResponseType},
        },
        channel::Reaction,
        gateway::Ready,
    },
    prelude::*,
};
use std::{env, sync::Arc};
use tokio::sync::RwLock;

struct Puissance4Game;

impl TypeMapKey for Puissance4Game {
    type Value = Puissance4GameData;
}

struct Handler;

#[async_trait]
impl EventHandler for Handler {
    async fn interaction_create(&self, ctx: Context, interaction: Interaction) {
        if let Interaction::ApplicationCommand(command) = interaction {
            let content = match command.data.name.as_str() {
                "puissance4" => match check_command_validity(&command) {
                    Ok(opponent) => {
                        let games_lock = {
                            let data_read = ctx.data.read().await;
                            data_read
                                .get::<Puissance4Game>()
                                .expect("Expected Puissance4Game in TypeMap")
                                .clone()
                        };

                        match setup_game(&ctx, games_lock, &command, opponent).await {
                            Ok(res) => res,
                            Err(e) => {
                                eprintln!("Error in game setup {e:?}");
                                String::from("Une erreur est survenue")
                            }
                        }
                    }
                    Err(e) => e,
                },
                "puissance4-classement" => {
                    command.defer(&ctx.http).await.unwrap();
                    let embed_builder = get_leaderbaord(&ctx).await;
                    command
                        .create_followup_message(&ctx.http, |response| response.embed(embed_builder))
                        .await
                        .unwrap();

                    return;
                }
                "dames" => "PAS ENCORE LÀ REVIENT PLUS TARD !!!".to_owned(),
                _ => "not implemented".to_owned(),
            };

            if let Err(e) = command
                .create_interaction_response(&ctx.http, |response| {
                    response
                        .kind(InteractionResponseType::ChannelMessageWithSource)
                        .interaction_response_data(|message| message.content(content).ephemeral(true))
                })
                .await
            {
                eprintln!("Cannot respond to slash command: {e:?}");
                return;
            }
        }
    }

    async fn reaction_add(&self, ctx: Context, reaction: Reaction) {
        if let Err(e) = reaction_added(ctx, reaction).await {
            eprintln!("Error managing reaction add: {e:?}");
        }
    }

    async fn ready(&self, ctx: Context, ready: Ready) {
        println!("{} is connected!", ready.user.name);

        Command::create_global_application_command(&ctx.http, |command| {
            command
                .name("puissance4")
                .description("Un jeu de Puissance 4")
                .create_option(|option| {
                    option
                        .name("adversaire")
                        .description("Votre adversaire au Puissance 4")
                        .kind(CommandOptionType::User)
                        .required(false)
                })
        })
        .await
        .unwrap();

        Command::create_global_application_command(&ctx.http, |command| {
            command
                .name("dames")
                .description("Un jeu de dames -- Arrive bientôt")
                .create_option(|option| {
                    option
                        .name("adversaire")
                        .description("Votre adversaire aux dames ")
                        .kind(CommandOptionType::User)
                        .required(true)
                })
        })
        .await
        .unwrap();

        Command::create_global_application_command(&ctx.http, |command| {
            command
                .name("puissance4-classement")
                .description("Le classement du Puissance 4")
        })
        .await
        .unwrap();
    }
}

#[tokio::main]
async fn main() {
    dotenv::dotenv().expect("Failed to load .env");

    let token = env::var("DISCORD_TOKEN").expect("Expected DISCORD_TOKEN in env");

    let mut client = Client::builder(token, GatewayIntents::GUILD_MESSAGE_REACTIONS)
        .event_handler(Handler)
        .await
        .expect("Error creating client");

    {
        let mut data = client.data.write().await;
        data.insert::<Puissance4Game>(Arc::new(RwLock::new(Vec::new())));
    }

    if let Err(e) = client.start().await {
        eprintln!("Client error: {e:?}");
    }
}
