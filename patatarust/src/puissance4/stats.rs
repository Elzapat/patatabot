use crate::puissance4::{Puissance4, Puissance4State};
use serde::{Deserialize, Serialize};
use serenity::{
    builder::CreateEmbed,
    model::id::{GuildId, UserId},
    prelude::*,
};
use std::{collections::HashMap, fs};

pub const LEADERBOARD_FILENAME: &str = "puissance4_stats.ron";
pub const PATATE_GUILD_ID: GuildId = GuildId(675349992130478080);

#[derive(Serialize, Deserialize, Debug, Default)]
pub struct Puissance4Stats {
    average_turns: f32,
    games_played: u32,
    total_turns: u64,
    player_stats: HashMap<UserId, PlayerStats>,
}

#[derive(Serialize, Deserialize, Debug, Default)]
struct PlayerStats {
    wins: u32,
    losses: u32,
    draws: u32,
    surrenders: Option<u32>,
    games_played: u32,
    total_turns: u64,
    average_turns: f32,
    matchups: HashMap<UserId, MatchupStats>,
}

#[derive(Serialize, Deserialize, Debug, Default)]
struct MatchupStats {
    wins_against: u32,
    losses_against: u32,
    draws_against: u32,
}

pub fn update_stats(game: &Puissance4) {
    let winner_id = game.players[game.playing].member.user.id;
    let loser_id = game.players[if game.playing == 1 { 0 } else { 1 }].member.user.id;
    let mut was_draw = false;
    let mut was_surrender = false;
    if let Puissance4State::Finished { draw, surrender } = game.state {
        was_draw = draw;
        was_surrender = surrender;
    }

    let stats_raw = fs::read_to_string(LEADERBOARD_FILENAME).unwrap();
    let mut stats: Puissance4Stats = match ron::from_str(&stats_raw) {
        Ok(stats) => stats,
        Err(e) => {
            eprintln!("Error reading stats file : {e:?}");
            return;
        }
    };

    stats.average_turns = (stats.average_turns + game.number_of_turns as f32) / 2.0;
    stats.total_turns += game.number_of_turns as u64;
    stats.games_played += 1;

    let winner_stats = stats.player_stats.entry(winner_id).or_insert_with(PlayerStats::default);
    winner_stats.games_played += 1;
    winner_stats.average_turns = (winner_stats.average_turns + game.number_of_turns as f32) / 2.0;
    winner_stats.total_turns += game.number_of_turns as u64;
    winner_stats.matchups.entry(loser_id).or_default().wins_against += 1;
    if was_draw {
        winner_stats.draws += 1;
        winner_stats.matchups.entry(winner_id).or_default().draws_against += 1;
    } else {
        winner_stats.wins += 1;
        winner_stats.matchups.entry(winner_id).or_default().wins_against += 1;
    }

    let loser_stats = stats.player_stats.entry(loser_id).or_insert_with(PlayerStats::default);
    loser_stats.games_played += 1;
    loser_stats.average_turns = (loser_stats.average_turns + game.number_of_turns as f32) / 2.0;
    loser_stats.total_turns += game.number_of_turns as u64;
    if was_draw {
        loser_stats.draws += 1;
        loser_stats.matchups.entry(loser_id).or_default().draws_against += 1;
    } else {
        loser_stats.losses += 1;
        loser_stats.matchups.entry(loser_id).or_default().losses_against += 1;
    }
    if was_surrender {
        loser_stats.surrenders = Some(loser_stats.surrenders.unwrap_or(0) + 1);
    }

    fs::write(LEADERBOARD_FILENAME, ron::to_string(&stats).unwrap()).unwrap();
}

pub async fn get_leaderbaord(ctx: &Context) -> impl FnOnce(&mut CreateEmbed) -> &mut CreateEmbed {
    let stats_raw = fs::read_to_string(LEADERBOARD_FILENAME).unwrap();
    let stats: Puissance4Stats = ron::from_str(&stats_raw).unwrap_or_default();
    let mut fields = Vec::new();

    let mut leaderboard = stats.player_stats.iter().collect::<Vec<_>>();
    leaderboard.sort_by(|(_, stats1), (_, stats2)| {
        let p1_wr = (stats1.wins as f32) / (stats1.games_played as f32);
        let p2_wr = (stats2.wins as f32) / (stats2.games_played as f32);
        p2_wr.partial_cmp(&p1_wr).unwrap()
    });

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
            format!(
                "```Victoires : {:<width$} Défaites         : {:<width$}\nÉgalités  : {:<width$} Taux de victoire : {:.2}%```",
                stats.wins,
                stats.losses,
                stats.draws,
                (stats.wins as f32 / stats.games_played as f32) * 100.0,
                width = 3,
            ),
            false,
        ));
    }

    let icon = PATATE_GUILD_ID.to_partial_guild(&ctx.http).await.unwrap().icon_url();

    move |mut embed| {
        if let Some(icon) = icon {
            embed = embed.author(|a| {
                a.icon_url(icon)
                    .name("Classement Puissance 4 (trié par taux de victoire)")
            });
        }

        embed
            // .title("Classement par victoires")
            .fields(fields)
            .color(serenity::utils::Color::GOLD)
    }
}
