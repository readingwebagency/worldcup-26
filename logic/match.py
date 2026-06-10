import random

def simulate_match(team_1, team_2, lookup_table, is_knockout=False):
    # 1. Ensure keys match the alphabetical lookup structure
    team_a, team_b = sorted([team_1, team_2])
    
    # 2. Instant O(1) Memory Lookup
    p_win_a, p_draw, p_win_b = lookup_table[(team_a, team_b)]
    
    r = random.random()
    
    # Heuristic 1 Proxy: Roll for a randomized goal margin if there is a winner
    margin_roll = random.random()
    if margin_roll < 0.65:
        margin = 1
    elif margin_roll < 0.90:
        margin = 2
    else:
        margin = 3
    
    # 3. Resolve Group Stage Matches (Draws allowed)
    if not is_knockout:
        if r < p_win_a:
            winner = team_a
            points = (3, 0) if winner == team_1 else (0, 3)
            # GD is relative to (team_1, team_2) order
            gd = (margin, -margin) if winner == team_1 else (-margin, margin)
            return {"winner": winner, "points": points, "gd": gd, "type": "win"}
            
        elif r < p_win_a + p_draw:
            return {"winner": "draw", "points": (1, 1), "gd": (0, 0), "type": "draw"}
            
        else:
            winner = team_b
            points = (3, 0) if winner == team_1 else (0, 3)
            gd = (margin, -margin) if winner == team_1 else (-margin, margin)
            return {"winner": winner, "points": points, "gd": gd, "type": "win"}
            
    # 4. Resolve Knockout Stage Matches (No Draws allowed)
    else:
        if r < p_win_a:
            # r is between 0.0 and p_win_a
            return {"winner": team_a, "type": "regulation_win"}
            
        elif r < (p_win_a + p_draw):
            # r is between p_win_a and (p_win_a + p_draw)
            # 🎯 Penalty Shootout Lottery: True 50/50 fair coin flip
            winner = random.choice([team_1, team_2])
            return {"winner": winner, "type": "penalty_draw"}
            
        else:
            # r is between (p_win_a + p_draw) and 1.0
            return {"winner": team_b, "type": "regulation_win"}