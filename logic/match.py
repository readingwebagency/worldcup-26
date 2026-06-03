import random

def simulate_match(team_1, team_2, lookup_table, is_knockout=False):
    # 1. Ensure keys match the alphabetical lookup structure
    team_a, team_b = sorted([team_1, team_2])
    
    # 2. Instant O(1) Memory Lookup
    p_win_a, p_draw, p_win_b = lookup_table[(team_a, team_b)]
    
    r = random.random()
    
    # 3. Resolve Group Stage Matches (Draws allowed)
    if not is_knockout:
        if r < p_win_a:
            return {"winner": team_a, "points": (3, 0), "type": "win"}
        elif r < p_win_a + p_draw:
            return {"winner": "draw", "points": (1, 1), "type": "draw"}
        else:
            return {"winner": team_b, "points": (0, 3), "type": "win"}
            
    # 4. Resolve Knockout Stage Matches (No Draws allowed)
    else:
        # Re-weight probabilities to exclude the draw
        total_win_prob = p_win_a + p_win_b
        p_knockout_a = p_win_a / total_win_prob
        
        if r < p_knockout_a:
            return {"winner": team_a, "type": "knockout_win"}
        else:
            return {"winner": team_b, "type": "knockout_win"}