from statsbombpy import sb
import pandas as pd

def get_competitions():
    return sb.competitions()

def get_matches(competition_id: int, season_id: int):
    return sb.matches(competition_id=competition_id, season_id=season_id)

def get_events(match_id: int):
    return sb.events(match_id=match_id)

def get_passes(match_id: int):
    events = get_events(match_id)
    passes = events[events["type"]=="Pass"].copy()
    passes = passes[passes["pass_outcome"].isna()] #succesful passes only
    return passes

def get_match_info(match_id: int, competition_id: int, season_id: int):
    matches = get_matches(competition_id, season_id)
    match = matches[matches["match_id"]== match_id].iloc[0]
    return {
        "home_team": match["home_team"],
        "away_team": match["away_team"],
        "score": f"{match['home_score']} - {match['away_score']}",
        "date": match["match_date"],
    }

def get_team_passes(match_id: int, team: str) -> pd.DataFrame:
    passes = get_passes(match_id)
    team_passes = passes[passes["team"] == team].copy()
    return team_passes

def get_starting_xi(match_id: int, team: str) -> list:
    events = get_events(match_id)
    lineups = events[
        (events["type"] == "Starting XI") &
        (events["team"] == team)
    ]
    if lineups.empty:
        return []
    lineup = lineups.iloc[0]["tactics"]["lineup"]
    return [p["player"]["name"] for p in lineup]

def get_team_passes_filtered(
    match_id: int,
    team: str,
    period: int = None,
    starting_xi_only: bool = False
) -> pd.DataFrame:

    passes = get_team_passes(match_id, team)

    if period is not None:
        passes = passes[passes["period"] == period].copy()

    if starting_xi_only:
        starting = get_starting_xi(match_id, team)
        if starting:
            passes = passes[passes["player"].isin(starting)].copy()

    return passes