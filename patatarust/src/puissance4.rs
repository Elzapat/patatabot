use crate::Puissance4Game;
use serenity::{
    model::{
        application::interaction::application_command::{ApplicationCommandInteraction, CommandDataOptionValue},
        channel::{Message, Reaction, ReactionType},
        guild::Member,
        id::{GuildId, UserId},
    },
    prelude::*,
};
use std::{collections::HashMap, error::Error, sync::Arc};
use tokio::sync::RwLock;

pub const GRID_WIDTH: u8 = 7;
pub const GRID_HEIGHT: u8 = 6;
pub const VALIDATE: char = '✅';
pub const CANCEL: char = '❌';
pub const LETTER_EMOJIS: [char; 26] = [
    '🇦', '🇧', '🇨', '🇩', '🇪', '🇫', '🇬', '🇭', '🇮', '🇯', '🇰', '🇱', '🇲', '🇳', '🇴', '🇵', '🇶', '🇷', '🇸', '🇹', '🇺', '🇻', '🇼',
    '🇽', '🇾', '🇿',
];

#[derive(Hash, Debug, Eq, PartialEq, Copy, Clone)]
pub struct Position {
    pub x: u8,
    pub y: u8,
}

impl Position {
    pub fn new(x: u8, y: u8) -> Self {
        Position { x, y }
    }
}

#[derive(Debug, Clone)]
pub struct Player {
    pub member: Member,
    pub symbol: char,
}

#[derive(Debug)]
pub struct Puissance4 {
    pub message: Message,
    pub number_players: usize,
    pub playing: usize,
    pub state: Puissance4State,
    pub players: [Player; 2],
    pub pawns: HashMap<Position, char>,
}

#[derive(Debug)]
pub enum Puissance4State {
    NotStarted,
    Started,
    Finished,
}

pub type Puissance4GameData = Arc<RwLock<Option<Puissance4>>>;

pub fn check_command_validity(command: &ApplicationCommandInteraction) -> Result<UserId, String> {
    let user_option = command
        .data
        .options
        .get(0)
        .expect("Expected user option")
        .resolved
        .as_ref()
        .expect("Expected user object");

    if let CommandDataOptionValue::User(user, _member) = user_option {
        Ok(user.id)
    } else {
        Err("Utilisateur inconnu".to_owned())
    }
}

pub async fn setup_game(
    ctx: &Context,
    game_lock: Puissance4GameData,
    command: &ApplicationCommandInteraction,
    opponent_user_id: UserId,
) -> Result<(), Box<dyn Error>> {
    let guild_id = command
        .guild_id
        .unwrap_or_else(|| GuildId(std::env::var("GUILD_ID").unwrap().parse::<u64>().unwrap()));
    let mut game = game_lock.write().await;
    if game.is_some() {
        command
            .channel_id
            .say(&ctx.http, "Une partie de puissance 4 est déjà en cours")
            .await?;
        return Ok(());
    }

    if let Ok(message) = command
        .channel_id
        .say(
            &ctx.http,
            format!(
                "<@{opponent_user_id}>, acceptes-tu le match de Puissance 4 contre <@{}>",
                command.user.id
            ),
        )
        .await
    {
        message
            .react(&ctx.http, ReactionType::Unicode(VALIDATE.to_string()))
            .await?;
        message
            .react(&ctx.http, ReactionType::Unicode(CANCEL.to_string()))
            .await?;

        *game = Some(Puissance4 {
            message,
            number_players: 2,
            playing: 0,
            state: Puissance4State::NotStarted,
            players: [
                Player {
                    member: guild_id.member(&ctx.http, command.user.id).await?,
                    symbol: '🟡',
                },
                Player {
                    member: guild_id.member(&ctx.http, opponent_user_id).await?,
                    symbol: '🔴',
                },
            ],
            pawns: HashMap::new(),
        });
    }

    Ok(())
}

pub async fn reaction_added(ctx: Context, reaction: Reaction) -> Result<(), Box<dyn Error>> {
    let game_lock = {
        let data_read = ctx.data.read().await;
        data_read
            .get::<Puissance4Game>()
            .expect("Expected Puissance4Game in TypeMap")
            .clone()
    };

    let mut game_opt = game_lock.write().await;

    if let Some(game) = &mut *game_opt {
        let mut message = reaction.channel_id.message(&ctx.http, reaction.message_id).await?;

        if message.id != game.message.id {
            return Ok(());
        }

        match game.state {
            Puissance4State::NotStarted => {
                if check_game_validation(&reaction, game.players[1].member.user.id) {
                    game.state = Puissance4State::Started;
                    message.delete_reactions(&ctx.http).await?;

                    message.edit(&ctx.http, |m| m.content(get_grid(game))).await?;

                    for emoji in &LETTER_EMOJIS[0..GRID_WIDTH as usize] {
                        message
                            .react(&ctx.http, ReactionType::Unicode(emoji.to_string()))
                            .await?;
                    }
                }
            }
            Puissance4State::Started => {
                if !reaction.user(&ctx.http).await?.bot {
                    reaction.delete(&ctx.http).await?;
                }

                if reaction.user_id.ok_or("No user in reaction")? == game.players[game.playing].member.user.id {
                    execute_turn(&ctx, &mut message, game, &reaction).await?;
                }
            }
            Puissance4State::Finished => {}
        }

        if let Puissance4State::Finished = game.state {
            *game_opt = None;
        }
    }

    Ok(())
}

pub async fn execute_turn(
    ctx: &Context,
    message: &mut Message,
    game: &mut Puissance4,
    reaction: &Reaction,
) -> Result<(), Box<dyn Error>> {
    if let ReactionType::Unicode(emoji) = &reaction.emoji {
        let reaction_emoji = emoji.chars().next().ok_or("Reaction emoji empty")?;

        if let Some(play_row) = LETTER_EMOJIS.iter().position(|&e| e == reaction_emoji) {
            let mut new_pawn_pos = Position::new(play_row as u8, 0);

            while game.pawns.contains_key(&new_pawn_pos) {
                new_pawn_pos.y += 1;
            }

            if new_pawn_pos.y < GRID_HEIGHT {
                game.pawns.insert(new_pawn_pos, game.players[game.playing].symbol);

                if check_victory(game, new_pawn_pos) {
                    game.state = Puissance4State::Finished;
                    message.delete_reactions(&ctx.http).await?;
                } else {
                    game.playing = (game.playing + 1) % game.number_players;
                }

                message.edit(&ctx.http, |m| m.content(get_grid(game))).await?;
            }
        }
    }

    Ok(())
}

fn check_victory(game: &Puissance4, pos: Position) -> bool {
    let check_left = pos.x > 2;
    let check_right = pos.x < GRID_WIDTH - 3;
    let check_down = pos.y > 2;
    let check_up = pos.y < GRID_HEIGHT - 3;
    let symbol = &game.players[game.playing].symbol;

    (check_left && check_side(game, |o| Position::new(pos.x - o, pos.y), symbol))
        || (check_right && check_side(game, |o| Position::new(pos.x + o, pos.y), symbol))
        || (check_up && check_side(game, |o| Position::new(pos.x, pos.y + o), symbol))
        || (check_down && check_side(game, |o| Position::new(pos.x, pos.y - o), symbol))
        || (check_left && check_up && check_side(game, |o| Position::new(pos.x - o, pos.y + o), symbol))
        || (check_up && check_right && check_side(game, |o| Position::new(pos.x + o, pos.y + o), symbol))
        || (check_right && check_down && check_side(game, |o| Position::new(pos.x + o, pos.y - o), symbol))
        || (check_down && check_left && check_side(game, |o| Position::new(pos.x - o, pos.y - o), symbol))
}

fn check_side<F: Fn(u8) -> Position>(game: &Puissance4, get_offset: F, symbol: &char) -> bool {
    (1..=3).map(get_offset).all(|pos| game.pawns.get(&pos) == Some(symbol))
}

pub fn check_game_validation(reaction: &Reaction, opp_id: UserId) -> bool {
    reaction.emoji == ReactionType::Unicode(VALIDATE.to_string()) && reaction.user_id == Some(opp_id)
}

pub fn get_grid(game: &Puissance4) -> String {
    let width = (2 * GRID_WIDTH) as usize - 1;
    let mut grid = match game.state {
        Puissance4State::Started => {
            format!(
                "{} ({}) vs {} ({})\nC'est au tour de {} ({})\n\n",
                game.players[0].member.display_name(),
                game.players[0].symbol,
                game.players[1].member.display_name(),
                game.players[1].symbol,
                game.players[game.playing].member.display_name(),
                game.players[game.playing].symbol,
            )
        }
        Puissance4State::Finished => {
            format!(
                "{} ({}) a gagné !\n\n",
                game.players[game.playing].member.display_name(),
                game.players[game.playing].symbol
            )
        }
        Puissance4State::NotStarted => String::new(),
    };

    grid.push('│');
    for letter in b'A'..b'A' + GRID_WIDTH {
        grid.push_str(&format!("{}│", LETTER_EMOJIS[(letter - b'A') as usize]));
    }
    grid.push_str("\n\n");

    /*
    for i in 0..=GRID_WIDTH * 2 {
        grid.push(match i {
            0 => '┌',
            i if i == GRID_WIDTH * 2 => '┐',
            i if i % 2 != 0 => '─',
            _ => '┬',
        });
    }
    grid.push('\n');
    */

    for y in (0..GRID_HEIGHT).rev() {
        grid.push('│');

        for x in 0..GRID_WIDTH {
            grid.push(if let Some(symbol) = game.pawns.get(&Position::new(x, y)) {
                *symbol
            } else {
                '⬛'
            });
            grid.push('│');
        }

        grid.push('\n');
    }

    /*
    for i in 0..=GRID_WIDTH * 2 {
        grid.push(match i {
            0 => '├',
            i if i == GRID_WIDTH * 2 => '┤',
            i if i % 2 != 0 => '─',
            _ => '┴',
        });
    }
    grid.push('\n');
    */

    grid
    // format!("{grid}┴{:width$}┴", "")
}
