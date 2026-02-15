#!/usr/bin/env python3
import nfl_data_py as nfl
import pandas as pd
import sys

def oppenent_defensive_strength(year):
    '''
    Calculates the average defensive strength (yards allowed) of each team's opponents
    for a given NFL season (regular season only)
    
    Input: 
        year (int): NFL season year
    Output:
        DataFrame: Team, avg opponent rush yards allowed, avg opponent pass yards allowed
    '''
    
    # Load schedule and weekly player stats
    schedule = nfl.import_schedules([year])
    schedule = schedule[schedule['week'] <= 18]  # Regular season only
    
    weekly = nfl.import_weekly_data([year])
    weekly = weekly[weekly['season_type'] == 'REG']  # Regular season only
    
    # Aggregate player stats to get TEAM OFFENSIVE totals by week
    team_offense_weekly = weekly.groupby(['recent_team', 'week', 'opponent_team']).agg({
        'rushing_yards': 'sum',
        'passing_yards': 'sum'
    }).reset_index()
    
    # Flip perspective: Team A's offensive yards against Team B = Team B's defensive yards allowed
    # So we group by opponent_team (the defense) to get yards allowed
    team_defense = team_offense_weekly.groupby('opponent_team').agg({
        'rushing_yards': 'sum',  # Total rush yards allowed all season
        'passing_yards': 'sum',  # Total pass yards allowed all season
        'week': 'count'  # Number of games
    }).reset_index()
    
    # Rename for clarity
    team_defense.columns = ['team', 'total_rush_yards_allowed', 'total_pass_yards_allowed', 'games']
    
    # Calculate per-game averages
    team_defense['rush_yards_allowed_per_game'] = team_defense['total_rush_yards_allowed'] / team_defense['games']
    team_defense['pass_yards_allowed_per_game'] = team_defense['total_pass_yards_allowed'] / team_defense['games']
    
    print("\nTeam defensive stats (yards allowed per game):")
    print(team_defense[['team', 'rush_yards_allowed_per_game', 'pass_yards_allowed_per_game']].head(10))
    
    # Now calculate opponent defensive strength for each team
    opponent_defense = {}
    teams = pd.concat([schedule['home_team'], schedule['away_team']]).unique()
    
    for team in teams:
        # Find all games this team played
        home_games = schedule[schedule['home_team'] == team]
        away_games = schedule[schedule['away_team'] == team]
        
        # Get their opponents
        home_opponents = home_games['away_team'].tolist()
        away_opponents = away_games['home_team'].tolist()
        all_opponents = home_opponents + away_opponents
        
        # Get defensive stats for those opponents
        opponent_stats = team_defense[team_defense['team'].isin(all_opponents)]
        
        # Calculate average defensive strength of opponents
        avg_rush_allowed = opponent_stats['rush_yards_allowed_per_game'].mean()
        avg_pass_allowed = opponent_stats['pass_yards_allowed_per_game'].mean()
        
        opponent_defense[team] = {
            'team': team,
            'avg_opp_rush_yards_allowed': avg_rush_allowed,
            'avg_opp_pass_yards_allowed': avg_pass_allowed,
            'num_opponents': len(all_opponents)
        }
    
    # Convert to DataFrame
    result_df = pd.DataFrame.from_dict(opponent_defense, orient='index')
    result_df = result_df.reset_index(drop=True)
    
    # Save to CSV
    result_df.to_csv(f'opponent_defense_{year}.csv', index=False)
    
    print(f"\n✓ Results saved to opponent_defense_{year}.csv")
    
    return result_df

def calculate_best_offense(year):
    '''
    Calculate the best NFL year offense for a given year, using defensive rating factors

    Input:
        year (int): NFL season year

    Output: 
        Dataframe: Teams ranked by adjusted offensive performance
    '''

    opponent_defense = oppenent_defensive_strength(year)

    weekly = nfl.import_weekly_data([year])
    weekly = weekly[weekly['season_type'] == 'REG']
    
    # Aggregate to team totals
    team_offense = weekly.groupby('recent_team').agg({
        'rushing_yards': 'sum',
        'passing_yards': 'sum',
        'week': 'nunique'  # count unique weeks = games played
    }).reset_index()
    
    team_offense.columns = ['team', 'total_rush_yards', 'total_pass_yards', 'games']
    
    # Calculate per-game averages
    team_offense['rush_yards_per_game'] = team_offense['total_rush_yards'] / team_offense['games']
    team_offense['pass_yards_per_game'] = team_offense['total_pass_yards'] / team_offense['games']
    team_offense['total_yards_per_game'] = team_offense['rush_yards_per_game'] + team_offense['pass_yards_per_game']
    
    
    # Merge with opponent defensive ratings
    combined = team_offense.merge(opponent_defense, on='team', how='inner')
    
    
    # Calculate adjusted ratings (performance relative to opponent strength)
    combined['adjusted_rush_rating'] = combined['rush_yards_per_game'] / combined['avg_opp_rush_yards_allowed']
    combined['adjusted_pass_rating'] = combined['pass_yards_per_game'] / combined['avg_opp_pass_yards_allowed']
    
    combined['offensive_score'] = (combined['adjusted_rush_rating'] * 0.4 + 
                                   combined['adjusted_pass_rating'] * 0.6)
    
    
    combined = combined.dropna(subset=['offensive_score'])
    combined = combined.sort_values('offensive_score', ascending=False).reset_index(drop=True)
    
    combined['rank'] = range(1, len(combined) + 1)
    
    combined.to_csv(f'best_offense_{year}.csv', index=False)
    print(f"\n✓ Full results saved to best_offense_{year}.csv\n")

    return combined

if __name__ == '__main__':
    year = int(input('Enter the year: '))
    best_offense = calculate_best_offense(year)
    top_team = best_offense.iloc[0]
    second_team = best_offense.iloc[1]

    print(f"\n🏆 BEST OFFENSE: {top_team['team']}")
    print(f"\n🏆 RUNNER-UP OFFENSE: {second_team['team']}")

