"""Canonical Premier League team names — maps football-data.co.uk + FPL API spellings
to one canonical name so the three sources can be joined. Apply to ALL historical data
before any join. canonicalize() returns the input unchanged if unknown (logs nothing)."""

# canonical = clean full club name
TEAM_ALIASES = {
    # --- football-data.co.uk short names ---
    'Man City': 'Manchester City',
    'Man United': 'Manchester United',
    "Nott'm Forest": 'Nottingham Forest',
    'Wolves': 'Wolverhampton Wanderers',
    'Hull': 'Hull City',
    'Leeds': 'Leeds United',
    'Newcastle': 'Newcastle United',
    'Brighton': 'Brighton and Hove Albion',
    'West Ham': 'West Ham United',
    'West Brom': 'West Bromwich Albion',
    'Leicester': 'Leicester City',
    'Ipswich': 'Ipswich Town',
    'Cardiff': 'Cardiff City',
    'Huddersfield': 'Huddersfield Town',
    'Norwich': 'Norwich City',
    'Stoke': 'Stoke City',
    'Swansea': 'Swansea City',
    'Tottenham': 'Tottenham',
    # --- FPL API spellings ---
    'Man Utd': 'Manchester United',
    'Spurs': 'Tottenham',
    'Sheffield Utd': 'Sheffield United',
    'Coventry City': 'Coventry City',
    'Hull City': 'Hull City',
    'Ipswich Town': 'Ipswich Town',
    'Leeds United': 'Leeds United',
    # --- pass-throughs / identity (canonical already) ---
    'Arsenal': 'Arsenal', 'Aston Villa': 'Aston Villa', 'Bournemouth': 'Bournemouth',
    'Brentford': 'Brentford', 'Burnley': 'Burnley', 'Chelsea': 'Chelsea',
    'Crystal Palace': 'Crystal Palace', 'Everton': 'Everton', 'Fulham': 'Fulham',
    'Liverpool': 'Liverpool', 'Middlesbrough': 'Middlesbrough',
    'Sheffield United': 'Sheffield United', 'Southampton': 'Southampton',
    'Sunderland': 'Sunderland', 'Watford': 'Watford',
    'Manchester City': 'Manchester City', 'Manchester United': 'Manchester United',
    'Newcastle United': 'Newcastle United', 'Nottingham Forest': 'Nottingham Forest',
    'Wolverhampton Wanderers': 'Wolverhampton Wanderers',
}

# The official 20 for 2026-27 (FPL-confirmed: Ipswich in, Wolves out)
PL_2026_27 = [
    'Arsenal', 'Aston Villa', 'Bournemouth', 'Brentford', 'Brighton and Hove Albion',
    'Chelsea', 'Coventry City', 'Crystal Palace', 'Everton', 'Fulham', 'Hull City',
    'Ipswich Town', 'Leeds United', 'Liverpool', 'Manchester City', 'Manchester United',
    'Newcastle United', 'Nottingham Forest', 'Sunderland', 'Tottenham',
]


def canonicalize(name):
    if name is None:
        return None
    return TEAM_ALIASES.get(str(name).strip(), str(name).strip())
