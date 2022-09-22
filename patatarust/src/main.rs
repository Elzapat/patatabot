mod puissance4;

use puissance4::{check_command_validity, reaction_added, setup_game, stats::get_leaderbaord, Puissance4GameData};
use serenity::{
    async_trait,
    builder::CreateInteractionResponseData,
    http::Http,
    model::{
        application::{
            command::{Command, CommandOptionType},
            interaction::{application_command::ApplicationCommandInteraction, Interaction, InteractionResponseType},
        },
        channel::Reaction,
        gateway::Ready,
    },
    prelude::*,
};
use std::{
    env,
    process::{Child, Command as StdCommand, Stdio},
    sync::Arc,
};
use tokio::sync::RwLock;

struct Puissance4Game;
impl TypeMapKey for Puissance4Game {
    type Value = Puissance4GameData;
}

struct PythonBot;
impl TypeMapKey for PythonBot {
    type Value = Arc<RwLock<Child>>;
}

struct Handler;

async fn respond_to_interaction<'a, F>(http: impl AsRef<Http>, command: ApplicationCommandInteraction, message: F)
where
    for<'b> F: FnOnce(&'b mut CreateInteractionResponseData<'a>) -> &'b mut CreateInteractionResponseData<'a>,
{
    if let Err(e) = command
        .create_interaction_response(http, |response| {
            response
                .kind(InteractionResponseType::ChannelMessageWithSource)
                .interaction_response_data(message)
        })
        .await
    {
        eprintln!("Error creating interaction response: {e:?}");
    }
}

#[async_trait]
impl EventHandler for Handler {
    async fn interaction_create(&self, ctx: Context, interaction: Interaction) {
        if let Interaction::ApplicationCommand(command) = interaction {
            /*
            ctx.http
                 .delete_global_application_command(command.data.id.into())
                 .await
                 .unwrap();
            ctx.http
                 .delete_guild_application_command(675349992130478080, command.data.id.into())
                 .await
                 .unwrap();
            ctx.http
                 .delete_guild_application_command(669507869791748117, command.data.id.into())
                 .await
                 .unwrap();
            */
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
                "boggle" => return,
                "dames" => "PAS ENCORE LÀ REVIENT PLUS TARD !!!".to_owned(),
                "mitsuki" | "gaspard" => return,
                _ => format!("{} not implemented", command.data.name),
            };

            respond_to_interaction(&ctx.http, command, |message| message.content(content).ephemeral(true)).await;
        }
    }

    async fn reaction_add(&self, ctx: Context, reaction: Reaction) {
        if let Err(e) = reaction_added(ctx, reaction).await {
            eprintln!("Error managing reaction add: {e:?}");
        }
    }

    async fn ready(&self, ctx: Context, ready: Ready) {
        println!("{} is connected! (Rust)", ready.user.name);

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

        /*
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
        */

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

    let intents = GatewayIntents::GUILD_MESSAGES
        | GatewayIntents::MESSAGE_CONTENT
        | GatewayIntents::GUILD_MESSAGE_REACTIONS;

    let mut client = Client::builder(token, intents)
        .event_handler(Handler)
        .await
        .expect("Error creating client");

    {
        let mut data = client.data.write().await;
        data.insert::<Puissance4Game>(Arc::new(RwLock::new(Vec::new())));
        data.insert::<PythonBot>(Arc::new(RwLock::new(
            StdCommand::new("python")
                .arg("../main.py")
                .stdin(Stdio::piped())
                // .stdout(Stdio::piped())
                .spawn()
                .unwrap(),
        )));
    }

    if let Err(e) = client.start().await {
        eprintln!("Client error: {e:?}");
    }
}
