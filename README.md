# NFL Best Offense Calculator - Work in Progress

A Python tool that identifies the best NFL offense for any given season by adjusting team performance based on the strength of defenses they faced.

## Project Status

This project is actively under development. Current functionality is working, but additional features are planned.

### Currently Working
- Calculate opponent defensive strength (rush & pass yards allowed)
- Aggregate team offensive statistics
- Adjust offensive performance based on opponent quality
- Generate rankings and CSV reports

### Planned Features
- Turnover analysis (fumbles, interceptions)
- Sack yards adjustment
- Red zone efficiency metrics
- Touchdown rate analysis
- Points per drive calculations
- Playoff game inclusion option
- Multi-year comparison tool
- Visualization/charts of rankings

## Overview

Unlike traditional rankings that only look at raw yards or points, this tool adjusts performance based on opponent defensive quality. A team that gains 300 yards against elite defenses should rank higher than a team gaining 300 yards against weak defenses.

## Methodology

1. **Opponent Defensive Strength**: For each team, calculate the average rushing and passing yards allowed by all their opponents during the season
2. **Adjusted Offensive Rating**: Divide each team's actual yards per game by their opponents' average yards allowed
   - Rating > 1.0 = performed better than opponents typically allow
   - Rating < 1.0 = performed worse than opponents typically allow
3. **Composite Score**: Weighted combination of adjusted rushing (40%) and passing (60%) ratings

## Requirements

- Python 3.11 (3.13 has compatibility issues with nfl_data_py)
- pandas
- nfl_data_py

## Installation

1. Create a conda environment:
```bash conda create -n  NFL_BEST python=3.11```