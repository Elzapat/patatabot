use crate::Puissance4Game;
use serde::{Deserialize, Serialize};
use serenity::{
    builder::CreateEmbed,
    model::{
        application::interaction::application_command::{ApplicationCommandInteraction, CommandDataOptionValue},
        channel::{Message, Reaction, ReactionType},
        guild::Member,
        id::{GuildId, UserId},
    },
    prelude::*,
};
use std::{collections::HashMap, default::Default, error::Error, fs, sync::Arc};
use tokio::sync::RwLock;

// Size of Puissance 4 grid
pub const LEADERBOARD_FILENAME: &str = "puissance4_stats.ron";
pub const PATATE_GUILD_ID: GuildId = GuildId(675349992130478080);
pub const GRID_WIDTH: i8 = 7;
pub const GRID_HEIGHT: i8 = 6;
pub const VALIDATE: char = '✅';
pub const CANCEL: char = '❌';
pub const LETTER_EMOJIS: [char; 26] = [
    '🇦', '🇧', '🇨', '🇩', '🇪', '🇫', '🇬', '🇭', '🇮', '🇯', '🇰', '🇱', '🇲', '🇳', '🇴', '🇵', '🇶', '🇷', '🇸', '🇹', '🇺', '🇻', '🇼',
    '🇽', '🇾', '🇿',
];

#[derive(Serialize, Deserialize, Debug)]
struct Puissance4Stats {
    average_turns: f32,
    player_stats: HashMap<UserId, PlayerStats>,
}

impl Default for Puissance4Stats {
    fn default() -> Self {
        Puissance4Stats {
            average_turns: 0.0,
            player_stats: HashMap::new(),
        }
    }
}

#[derive(Serialize, Deserialize, Debug)]
struct PlayerStats {
    wins: u32,
    losses: u32,
    average_turns: f32,
    matchups: HashMap<UserId, u32>,
}

impl Default for PlayerStats {
    fn default() -> Self {
        PlayerStats {
            wins: 0,
            losses: 0,
            average_turns: 0.0,
            matchups: HashMap::new(),
        }
    }
}

// Struct representing a position on the grid
#[derive(Hash, Debug, Eq, PartialEq, Copy, Clone)]
pub struct Position {
    pub x: i8,
    pub y: i8,
}

impl Position {
    pub fn new(x: i8, y: i8) -> Self {
        Position { x, y }
    }
}

// A Puissse 4 player
#[derive(Debug, Clone)]
pub struct Player {
    pub member: Member,
    pub symbol: char,
}

// Struct representing a runnig game of Puissance 4
#[derive(Debug)]
pub struct Puissance4 {
    pub free_opponent: bool,
    pub message: Message,
    pub number_players: usize,
    pub playing: usize,
    pub state: Puissance4State,
    pub players: [Player; 2],
    pub pawns: HashMap<Position, char>,
    number_of_turns: u32,
}

// State of the Puissance 4 game
#[derive(Debug)]
pub enum Puissance4State {
    NotStarted,
    Started,
    Finished,
}

pub type Puissance4GameData = Arc<RwLock<Vec<Puissance4>>>;

// Check if the command to start the game is valid, by checking if the argument is a correct user
pub fn check_command_validity(command: &ApplicationCommandInteraction) -> Result<Option<UserId>, String> {
    if let Some(arg) = command.data.options.get(0) {
        if let CommandDataOptionValue::User(user, _member) = arg.resolved.as_ref().expect("Expected user object") {
            Ok(Some(user.id))
        } else {
            Err("Utilisateur inconnu".to_owned())
        }
    } else {
        Ok(None)
    }
}

// Sets up the game, asking the opponent a confirmation and instancing the Puissance4 struct
pub async fn setup_game(
    ctx: &Context,
    game_lock: Puissance4GameData,
    command: &ApplicationCommandInteraction,
    opponent: Option<UserId>,
) -> Result<String, Box<dyn Error>> {
    let guild_id = command
        .guild_id
        .unwrap_or_else(|| GuildId(std::env::var("GUILD_ID").unwrap().parse::<u64>().unwrap()));
    let mut games = game_lock.write().await;

    if let Some(opponent_user_id) = opponent {
        for game in games.iter() {
            if game.players[0].member.user.id == command.user.id || game.players[1].member.user.id == command.user.id {
                return Ok("Tu es déjà en train de jouer une partie".to_owned());
            }

            if game.players[0].member.user.id == opponent_user_id || game.players[1].member.user.id == opponent_user_id
            {
                return Ok("L'adversaire est déjà en train de jouer une partie".to_owned());
            }
        }

        if opponent_user_id.to_user(&ctx.http).await?.bot {
            return Ok("Tu ne peux pas faire une partie contre un bot".to_owned());
        }
    }

    if let Ok(message) = command
        .channel_id
        .say(
            &ctx.http,
            match opponent {
                Some(opponent_user_id) => format!(
                    "<@{opponent_user_id}>, acceptes-tu le match de Puissance 4 contre <@{}>",
                    command.user.id
                ),
                None => format!(
                    "<@{}> recherche un adversaire pour faire un Puissance 4",
                    command.user.id
                ),
            },
        )
        .await
    {
        message
            .react(&ctx.http, ReactionType::Unicode(VALIDATE.to_string()))
            .await?;
        message
            .react(&ctx.http, ReactionType::Unicode(CANCEL.to_string()))
            .await?;

        games.push(Puissance4 {
            free_opponent: opponent.is_none(),
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
                    member: guild_id.member(&ctx.http, opponent.unwrap_or(command.user.id)).await?,
                    symbol: '🔴',
                },
            ],
            pawns: HashMap::new(),
            number_of_turns: 0,
        });
    }

    Ok("La partie est en cours de préapartion...".to_owned())
}

// Manages a new reaction on a message
pub async fn reaction_added(ctx: Context, reaction: Reaction) -> Result<(), Box<dyn Error>> {
    let games_lock = {
        let data_read = ctx.data.read().await;
        data_read
            .get::<Puissance4Game>()
            .expect("Expected Puissance4Game in TypeMap")
            .clone()
    };

    let mut message = reaction.channel_id.message(&ctx.http, reaction.message_id).await?;
    let mut games = games_lock.write().await;
    let mut idx = 0;

    while idx < games.len() {
        let game = &mut games[idx];

        if message.id != game.message.id {
            continue;
        }

        if !reaction.user(&ctx.http).await?.bot {
            reaction.delete(&ctx.http).await?;
        } else {
            return Ok(());
        }

        match game.state {
            Puissance4State::NotStarted => {
                if check_game_validation(
                    &reaction,
                    game.players[if game.free_opponent { 0 } else { 1 }].member.user.id,
                    game.free_opponent,
                ) {
                    if game.free_opponent {
                        game.players[1].member = reaction
                            .guild_id
                            .unwrap()
                            .member(&ctx.http, reaction.user_id.unwrap())
                            .await?;
                    }

                    game.state = Puissance4State::Started;
                    message.delete_reactions(&ctx.http).await?;

                    message.edit(&ctx.http, |m| m.content(get_grid(game))).await?;

                    for emoji in &LETTER_EMOJIS[0..GRID_WIDTH as usize] {
                        message
                            .react(&ctx.http, ReactionType::Unicode(emoji.to_string()))
                            .await?;
                    }
                } else if check_game_cancel(&reaction, &game.players) {
                    games.remove(idx);
                    message.edit(&ctx.http, |m| m.content("Partie refusée.")).await?;
                    message.delete_reactions(&ctx.http).await?;
                    continue;
                }
            }
            Puissance4State::Started => {
                if reaction.user_id.ok_or("No user in reaction")? == game.players[game.playing].member.user.id {
                    execute_turn(&ctx, &mut message, game, &reaction).await?;
                }
            }
            Puissance4State::Finished => {}
        }

        if let Puissance4State::Finished = game.state {
            games.remove(idx);
            continue;
        }

        idx += 1;
    }

    Ok(())
}

pub async fn execute_turn(
    ctx: &Context,
    message: &mut Message,
    game: &mut Puissance4,
    reaction: &Reaction,
) -> Result<(), Box<dyn Error>> {
    game.number_of_turns += 1;

    if let ReactionType::Unicode(emoji) = &reaction.emoji {
        let reaction_emoji = emoji.chars().next().ok_or("Reaction emoji empty")?;

        if let Some(play_row) = LETTER_EMOJIS.iter().position(|&e| e == reaction_emoji) {
            let mut new_pawn_pos = Position::new(play_row as i8, 0);

            while game.pawns.contains_key(&new_pawn_pos) {
                new_pawn_pos.y += 1;
            }

            if new_pawn_pos.y < GRID_HEIGHT {
                game.pawns.insert(new_pawn_pos, game.players[game.playing].symbol);

                if check_victory(game, new_pawn_pos) {
                    game.state = Puissance4State::Finished;
                    message.delete_reactions(&ctx.http).await?;
                    update_stats(game);
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
    let check_left = pos.x > 1;
    let check_right = pos.x < GRID_WIDTH - 2;
    let check_down = pos.y > 1;
    let check_up = pos.y < GRID_HEIGHT - 2;
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

fn check_side<F: Fn(i8) -> Position>(game: &Puissance4, get_offset: F, symbol: &char) -> bool {
    (0..=3).map(&get_offset).all(|pos| game.pawns.get(&pos) == Some(symbol))
        || (-1..=2).map(get_offset).all(|pos| game.pawns.get(&pos) == Some(symbol))
}

fn check_game_validation(reaction: &Reaction, opp_id: UserId, free_opp: bool) -> bool {
    (free_opp && reaction.user_id != Some(opp_id))
        || (reaction.emoji == ReactionType::Unicode(VALIDATE.to_string()) && reaction.user_id == Some(opp_id))
}

fn check_game_cancel(reaction: &Reaction, players: &[Player; 2]) -> bool {
    reaction.emoji == ReactionType::Unicode(CANCEL.to_string())
        && (reaction.user_id == Some(players[0].member.user.id) || reaction.user_id == Some(players[1].member.user.id))
}

fn get_grid(game: &Puissance4) -> String {
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
    for letter in b'A'..b'A' + GRID_WIDTH as u8 {
        grid.push_str(&format!("{}│", LETTER_EMOJIS[(letter - b'A') as usize]));
    }
    grid.push_str("\n\n");

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

    grid
}

fn update_stats(game: &Puissance4) {
    let winner_id = game.players[game.playing].member.user.id;
    let loser_id = game.players[if game.playing == 1 { 0 } else { 1 }].member.user.id;

    let stats_raw = fs::read_to_string(LEADERBOARD_FILENAME).unwrap();
    let mut stats: Puissance4Stats = match ron::from_str(&stats_raw) {
        Ok(stats) => stats,
        Err(e) => {
            eprintln!("Error reading stats file : {e:?}");
            return;
        }
    };

    stats.average_turns = (stats.average_turns + game.number_of_turns as f32) / 2.0;

    let winner_stats = stats.player_stats.entry(winner_id).or_insert_with(PlayerStats::default);
    winner_stats.wins += 1;
    winner_stats.average_turns = (winner_stats.average_turns + game.number_players as f32) / 2.0;
    *winner_stats.matchups.entry(winner_id).or_insert(0) += 1;

    let loser_stats = stats.player_stats.entry(loser_id).or_insert_with(PlayerStats::default);
    loser_stats.losses += 1;
    loser_stats.average_turns = (loser_stats.average_turns + game.number_players as f32) / 2.0;
    *loser_stats.matchups.entry(loser_id).or_insert(0) += 1;

    fs::write(LEADERBOARD_FILENAME, ron::to_string(&stats).unwrap()).unwrap();
}

pub async fn get_leaderbaord(ctx: &Context) -> impl FnOnce(&mut CreateEmbed) -> &mut CreateEmbed {
    let stats_raw = fs::read_to_string(LEADERBOARD_FILENAME).unwrap();
    let stats: Puissance4Stats = ron::from_str(&stats_raw).unwrap_or_default();
    let mut fields = Vec::new();

    let mut leaderboard = stats.player_stats.iter().collect::<Vec<_>>();
    leaderboard.sort_by(|(_, stats1), (_, stats2)| stats1.wins.cmp(&stats2.wins));

    for (rank, (user_id, stats)) in leaderboard.iter().enumerate() {
        if rank > 10 {
            break;
        }

        let user = user_id.to_user(&ctx.http).await.unwrap();

        fields.push((
            format!(
                "#{} {} ({})",
                rank + 1,
                user.nick_in(&ctx.http, PATATE_GUILD_ID).await.unwrap(),
                user.name,
            ),
            format!("`Victoires : {:<4}  Défaites : {}`", stats.wins, stats.losses),
            false,
        ));
    }

    let icon = PATATE_GUILD_ID.to_partial_guild(&ctx.http).await.unwrap().icon_url();

    move |mut embed| {
        if let Some(icon) = icon {
            embed = embed.author(|a| a.icon_url(icon).name("Classement Puissance 4"));
        }

        embed
            // .title("Classement par victoires")
            .fields(fields)
            .color(serenity::utils::Color::GOLD)
    }
}
