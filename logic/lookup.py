import json
from elo import outcome_probs

HOME_ADVANTAGE = 100  # Standard Elo boost given to host nations

def build_lookup_table(teams_json_path):
    with open(teams_json_path, 'r') as f:
        teams = json.load(f)
        
    lookup = {}
    num_teams = len(teams)
    
    # Calculate all 1,128 unique combinations
    for i in range(num_teams):
        for j in range(i + 1, num_teams):
            team_1 = teams[i]
            team_2 = teams[j]
            
            # Apply Home Field Advantage to baseline ratings if applicable
            r1 = team_1["rating"] + (HOME_ADVANTAGE if team_1["isHome"] else 0)
            r2 = team_2["rating"] + (HOME_ADVANTAGE if team_2["isHome"] else 0)
            
            # Alpha-sort keys so ("England", "Spain") and ("Spain", "England") map to the same row
            team_a, team_b = sorted([team_1["name"], team_2["name"]])
            
            # Get probabilities from the perspective of team_a vs team_b
            if team_a == team_1["name"]:
                p_win_a, p_draw, p_win_b = outcome_probs(r1, r2)
            else:
                p_win_a, p_draw, p_win_b = outcome_probs(r2, r1)
                
            lookup[(team_a, team_b)] = (p_win_a, p_draw, p_win_b)
            
    return lookup