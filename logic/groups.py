# logic/groups.py
import json

def get_group_fixture_probabilities(group_letter, fixtures_json_path="data/fixtures.json", lookup_json_path="data/lookup_table.json"):
    """
    Reads from the pre-generated static JSON lookup matrix instantly.
    """
    # 1. Load the pre-calculated matrix
    try:
        with open(lookup_json_path, 'r') as f:
            lookup_table = json.load(f)
    except FileNotFoundError:
        print(f"❌ Error: '{lookup_json_path}' not found. Please run 'python main.py generate' first.")
        return []

    # 2. Load fixtures
    with open(fixtures_json_path, 'r') as f:
        fixtures = json.load(f)
        
    group_letter = group_letter.upper()
    group_fixtures = [m for m in fixtures if m["group"].upper() == group_letter]
    
    if not group_fixtures:
        return []
        
    group_fixtures.sort(key=lambda x: x["date"])
    group_probabilities = []
    
    for match in group_fixtures:
        home_team = match["home"]
        away_team = match["away"]
        
        team_a, team_b = sorted([home_team, away_team])
        
        # Query using the pre-formatted string key
        lookup_key = f"{team_a} vs {team_b}"
        p_a_win, p_draw, p_b_win = lookup_table[lookup_key]
        
        if home_team == team_a:
            p_home_win, p_away_win = p_a_win, p_b_win
        else:
            p_home_win, p_away_win = p_b_win, p_a_win
            
        group_probabilities.append({
            "date": match["date"],
            "home": home_team,
            "away": away_team,
            "p_home_win": p_home_win,
            "p_draw": p_draw,
            "p_away_win": p_away_win
        })
        
    return group_probabilities