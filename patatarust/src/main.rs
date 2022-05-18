use std::env;
use serenity::{
    async_trait, prelude::*,
    model::{
        gateway::Ready, id::GuildId,
        application::{
            command::{Command, CommandOptionType},
            interaction::{
                application_command::CommandDataOptionValue,
                Interaction, InteractionResponseType,
            }
        },
    }
};

struct Handler;

#[async_trait]
impl EventHandler for Handler {
    async fn interaction_create(&self, ctx: Context, interaction: Interaction) {
        if let Interaction::ApplicationCommand(command) = interaction {
            let content = match command.data.name.as_str() {
                "puissance4" => {
                    "test".to_owned()
                }
            };

            if let Err(e) = command.create_interaction_response(&ctx.http, |response| {
                response.kind(InteractionResponseType::ChannelMessageWithSource)
                    .interaction_response_data(|message| message.content(message))
            })
            .await
            {

            }
        }
    }

    async fn ready(&self, ctx: Context, ready: Ready) {
        println!("{} is connected!", ready.user.name);

        let guild_id = GuildId(
            env::var("GUILD_ID")
                .expect("Expected GUILD_ID in env")
                .parse()
                .expect("GUILD_ID must be an integer")
        );

        let commands = GuildId::set_application_commands(&guild_id, &ctx.http, |commands| {
            commands
                .create_application_command(|command| {
                    command.name("puissance4").description("Un jeu de Puissance 4").create_option(|option| {
                        option
                            .name("adversaire")
                            .description("Votre adversaire au Puissance 4")
                            .kind(CommandOptionType::User)
                            .required(true)
                    })
                })
        }).await;

        println!("I now have the following slash commands: {commands:#?}");
    }
}

#[tokio::main]
async fn main() {
    dotenv::dotenv().expect("Failed to load .env");

    let token = env::var("DISCORD_TOKEN").expect("Expected DISCORD_TOKEN in env");

    let mut client = Client::builder(token, GatewayIntents::empty())
        .event_handler(Handler)
        .await
        .expect("Error creating client");

    if let Err(e) = client.start().await {
        eprintln!("Client error: {e:?}");
    }
}
