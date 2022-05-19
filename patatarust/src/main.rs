mod puissance4;

use puissance4::*;
use serenity::{
    async_trait,
    model::{
        application::{
            command::{Command, CommandOptionType},
            interaction::{Interaction, InteractionResponseType},
        },
        channel::Reaction,
        gateway::Ready,
        id::GuildId,
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
            let mut start_game = None;

            let content = match command.data.name.as_str() {
                "puissance4" => match check_command_validity(&command) {
                    Ok(opponent_user_id) => {
                        start_game = Some(opponent_user_id);
                        "La partie est en cours de préparation...".to_owned()
                    }
                    Err(e) => e,
                },
                _ => "not implemented".to_owned(),
            };

            if let Err(e) = command
                .create_interaction_response(&ctx.http, |response| {
                    response
                        .kind(InteractionResponseType::ChannelMessageWithSource)
                        .interaction_response_data(|message| message.content(content))
                })
                .await
            {
                eprintln!("Cannot respond to slash command: {e:?}");
                return;
            }

            if let Some(opponent_user_id) = start_game {
                let game_lock = {
                    let data_read = ctx.data.read().await;
                    data_read
                        .get::<Puissance4Game>()
                        .expect("Expected Puissance4Game in TypeMap")
                        .clone()
                };

                if let Err(e) = setup_game(&ctx, game_lock, &command, opponent_user_id).await {
                    eprintln!("Error in game setup {e:?}");
                }
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

        let guild_id = GuildId(
            env::var("GUILD_ID")
                .expect("Expected GUILD_ID in env")
                .parse()
                .expect("GUILD_ID must be an integer"),
        );

        let command = Command::create_global_application_command(&ctx.http, |command| {
            command
                .name("puissance4")
                .description("Un jeu de Puissance 4")
                .create_option(|option| {
                    option
                        .name("adversaire")
                        .description("Votre adversaire au Puissance 4")
                        .kind(CommandOptionType::User)
                        .required(true)
                })
        })
        .await;

        println!("I now have the following slash commands: {command:#?}");
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
        data.insert::<Puissance4Game>(Arc::new(RwLock::new(None)));
    }

    if let Err(e) = client.start().await {
        eprintln!("Client error: {e:?}");
    }
}
