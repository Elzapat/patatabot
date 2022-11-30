use rand::Rng;
use serde::{Deserialize, Serialize};
use serde_json::value::Value;
use serenity::{
    model::{
        application::interaction::application_command::ApplicationCommandInteraction,
        id::{GuildId, UserId},
    },
    prelude::*,
};
use std::{collections::HashSet, error::Error, fs};

const SECRET_SANTA_FILE: &str = "assets/secret_santa.ron";

#[derive(Debug, Copy, Clone, Hash, Eq, Serialize, Deserialize)]
struct Participant {
    user_id: UserId,
    giftee_id: Option<UserId>,
}

impl Participant {
    fn new(user_id: UserId) -> Participant {
        Participant {
            user_id,
            giftee_id: None,
        }
    }
}

impl PartialEq for Participant {
    fn eq(&self, other: &Self) -> bool {
        self.user_id == other.user_id
    }
}

#[derive(Debug, Serialize, Deserialize)]
struct SecretSanta {
    participants: HashSet<Participant>,
    participants_distributed: Option<HashSet<Participant>>,
}

pub fn secret_santa(command: &ApplicationCommandInteraction) -> (bool, String) {
    if let Some(Value::String(action)) = &command.data.options[0].value {
        match action.as_str() {
            "enter" => {
                let result = enter(command.user.id);
                (
                    result.is_err(),
                    match result {
                        Ok(_) => "Tu as été inscrit.",
                        Err(e) => {
                            eprintln!("Error {e:?} in secret-santa enter");
                            "Tu n'as pas été inscrit à cause d'une erreur"
                        }
                    }
                    .to_owned(),
                )
            }
            "leave" => {
                let result = leave(command.user.id);
                (
                    result.is_err(),
                    match result {
                        Ok(_) => "Tu as été désinscrit.",
                        Err(e) => {
                            eprintln!("Error {e:?} in secret-santa leave");
                            "Tu n'as pas été désinscrit à cause d'une erreur"
                        }
                    }
                    .to_owned(),
                )
            }
            "list" => {
                let result = list_participants();
                (
                    result.is_err(),
                    match result {
                        Ok(message) => message,
                        Err(e) => {
                            eprintln!("Error {e:?} in secret-santa list");
                            "Une erreur est survenue, pas de chance".to_owned()
                        }
                    },
                )
            }
            "start" => {
                let result = start();
                (
                    result.is_err(),
                    match result {
                        Ok(message) => message,
                        Err(e) => {
                            eprintln!("Error {e:?} in secret-santa start");
                            "Une erreur est survenue, pas de chance".to_owned()
                        }
                    },
                )
            }
            _ => unreachable!(),
        }
    } else {
        (true, "Erreur interne bizarre, c'est pas normal".to_owned())
    }
}

fn get_secret_santa() -> Result<SecretSanta, Box<dyn Error>> {
    let secret_santa = fs::read_to_string(SECRET_SANTA_FILE)?;
    Ok(ron::from_str(&secret_santa)?)
}

fn write_secret_santa(secret_santa: SecretSanta) -> Result<(), Box<dyn Error>> {
    fs::write(SECRET_SANTA_FILE, ron::to_string(&secret_santa)?)?;
    Ok(())
}

fn enter(user_id: UserId) -> Result<(), Box<dyn Error>> {
    let mut secret_santa = get_secret_santa()?;
    secret_santa.participants.insert(Participant::new(user_id));
    write_secret_santa(secret_santa)?;

    Ok(())
}

fn leave(user_id: UserId) -> Result<(), Box<dyn Error>> {
    let mut secret_santa = get_secret_santa()?;
    secret_santa.participants.remove(&Participant::new(user_id));
    write_secret_santa(secret_santa)?;

    Ok(())
}

fn list_participants() -> Result<String, Box<dyn Error>> {
    let secret_santa = get_secret_santa()?;
    let mut message = "Liste des participants du Secret Santa © Patate Edition ®©TM 2022:".to_owned();

    if secret_santa.participants.is_empty() {
        message += "\n\nPERSONNE <:JeanMarie_Elard:708061398529343529>";
    } else {
        for participant in secret_santa.participants {
            message = format!("{}\n > {{{}}}", message, participant.user_id.to_string());
        }
    }

    Ok(message)
}

fn start() -> Result<String, Box<dyn Error>> {
    let mut secret_santa = get_secret_santa()?;
    let mut secret_santa_distributed = HashSet::new();
    let mut rng = rand::thread_rng();

    let random_index = rng.gen_range(0..secret_santa.participants.len());
    let og_gifter = secret_santa.participants.iter().nth(random_index).unwrap().clone();
    secret_santa.participants.remove(&og_gifter);

    let mut gifter = og_gifter;
    let mut giftee;

    while !secret_santa.participants.is_empty() {
        let random_index = rng.gen_range(0..secret_santa.participants.len());
        giftee = secret_santa.participants.iter().nth(random_index).unwrap().clone();
        secret_santa.participants.remove(&giftee);

        gifter.giftee_id = Some(giftee.user_id);
        secret_santa_distributed.insert(gifter);

        gifter = giftee;
    }

    gifter.giftee_id = Some(og_gifter.user_id);
    secret_santa_distributed.insert(gifter);

    secret_santa.participants_distributed = Some(secret_santa_distributed);
    write_secret_santa(secret_santa)?;

    Ok("La distribution à été faite (normalement)".to_owned())
}

pub async fn substitute_ids(ctx: &Context, guild_id: GuildId, message: &mut String) {
    let mut result = message.clone();

    for line in message.lines() {
        if let Some(start) = line.find("{") {
            let end = line.find("}").unwrap_or(line.len());
            let id = &line[start + 1..end].parse::<UserId>().unwrap();
            let name = guild_id
                .member(&ctx.http, id)
                .await
                .unwrap()
                .nick
                .unwrap_or("prout".to_owned());

            result = result.replace(&format!("{{{id}}}"), &name);
        }
    }

    *message = result;
}

pub async fn send_giftees(ctx: &Context, guild_id: GuildId) {
    let secret_santa = get_secret_santa().unwrap();

    for participant in secret_santa.participants_distributed.unwrap().iter() {
        if let Some(giftee_id) = participant.giftee_id {
            let gifter_member = guild_id.member(&ctx.http, participant.user_id).await.unwrap();

            let giftee_member = guild_id.member(&ctx.http, giftee_id).await.unwrap();
            let giftee_name = giftee_member.nick.unwrap_or(giftee_member.user.name);

            gifter_member
                .user
                .direct_message(&ctx.http, |m| {
                    m.content(format!("La personne a qui tu dois offrir un cadeau est {giftee_name}"))
                })
                .await
                .unwrap();
        }
    }
}
