from lookup import build_lookup_table
from match import simulate_match

# 1. Build cache once
lookup_table = build_lookup_table("teams.json")

# 2. Run your 10,000 simulations
for sim in range(10000):
    # --- Example Group Match ---
    res = simulate_match("England", "France", lookup_table, is_knockout=False)
    
    # --- Example Knockout Match ---
    res_ko = simulate_match("England", "Spain", lookup_table, is_knockout=True)