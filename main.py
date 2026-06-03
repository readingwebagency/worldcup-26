import json
from datetime import datetime
from logic.lookup import build_lookup_table

def print_group_fixtures_with_probs(group_letter, lookup_table, fixtures_json_path="data/fixtures.json"):
    # 1. Load the chronological fixtures file
    with open(fixtures_json_path, 'r') as f:
        fixtures = json.load(f)
        
    # 2. Filter matches only belonging to our target group
    group_letter = group_letter.upper()
    group_fixtures = [m for m in fixtures if m["group"].upper() == group_letter]
    
    if not group_fixtures:
        print(f"No fixtures found for Group {group_letter}!")
        return
        
    # 3. Sort the group fixtures by date so they print in chronological order
    group_fixtures.sort(key=lambda x: x["date"])
    
    print("=============================================")
    print(f"     CHRONOLOGICAL PROBABILITIES: GROUP {group_letter}     ")
    print("=============================================\n")
    
    for match in group_fixtures:
        date_str = match["date"]
        home_team = match["home"]
        away_team = match["away"]
        
        # Turn "2026-06-11" into a readable string like "June 11, 2026"
        date_obj = datetime.strptime(date_str, "%Y-%m-%d")
        formatted_date = date_obj.strftime("%B %d, %Y")
        
        # Alphabetically sort the team names to match the lookup table key structure perfectly
        team_a, team_b = sorted([home_team, away_team])
        p_a_win, p_draw, p_b_win = lookup_table[(team_a, team_b)]
        
        # We need to map the alphabetical "Team A vs Team B" values back to the 
        # actual "Home vs Away" perspective defined in fixtures.json
        if home_team == team_a:
            p_home_win = p_a_win
            p_away_win = p_b_win
        else:
            p_home_win = p_b_win
            p_away_win = p_a_win
            
        # Print out the match details cleanly
        print(f"📅 {formatted_date}")
        print(f"   {home_team} (Home) vs. {away_team} (Away)")
        print(f"   └─ {home_team} Win: {p_home_win * 100:.1f}% | Draw: {p_draw * 100:.1f}% | {away_team} Win: {p_away_win * 100:.1f}%")
        print("-" * 50)

def main():
    # Build your protected-draw table once
    print("Initializing lookup engine...")
    lookup_table = build_lookup_table("data/teams.json")
    print("Lookup table active.\n")
    
    # Target and inspect Group A's schedule
    print_group_fixtures_with_probs("A", lookup_table)

if __name__ == "__main__":
    main()