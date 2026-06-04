# logic/generate_data.py
import json
import os
from logic.lookup import build_lookup_table

def generate_lookup_json(teams_json_path="data/teams.json", output_json_path="data/lookup_table.json"):
    """
    Builds the 1,128 team combinations matrix and saves it as a static JSON file.
    """
    print("🔄 Generating baseline ELO probability matrix...")
    
    # 1. Reuse your existing function to get the dictionary matrix
    tuple_lookup = build_lookup_table(teams_json_path)
    
    # 2. Convert tuple keys ("Team A", "Team B") into string keys "Team A vs Team B"
    string_lookup = {}
    for (team_a, team_b), probs in tuple_lookup.items():
        key_str = f"{team_a} vs {team_b}"
        string_lookup[key_str] = probs # [p_win_a, p_draw, p_win_b]
        
    # 3. Ensure the data directory exists and dump the JSON
    os.makedirs(os.path.dirname(output_json_path), exist_ok=True)
    with open(output_json_path, 'w') as f:
        json.dump(string_lookup, f, indent=4)
        
    print(f"✅ Success! Static lookup table saved to '{output_json_path}'")