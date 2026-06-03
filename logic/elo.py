import math

# --- Your Constrained Cubic Configuration ---
MAX_DRAW = 0.28  
C_PARAM = 0.15   
SCALE = 600      

def win_probability(ri, rj):
    dr = ri - rj
    return 1 / (10 ** (-dr / 400) + 1)

def get_draw_rate(ri, rj):
    diff = abs(ri - rj)
    x = diff / SCALE
    
    if x >= 1.0:
        return 0.0
        
    p_draw = MAX_DRAW * (1 - x**2) + C_PARAM * (x**2 - x**3)
    return max(0.0, p_draw)

def outcome_probs(ri, rj):
    # 1. Get the absolute draw rate. This is now locked and unchangeable.
    p_draw = get_draw_rate(ri, rj)
    
    # 2. Calculate the total pool of probability left over for actual wins/losses
    remaining_equity = 1.0 - p_draw
    
    # 3. Find the raw, relative ratio of strength between the two teams
    w_exp_a = win_probability(ri, rj)
    w_exp_b = 1.0 - w_exp_a
    
    # 4. Distribute ONLY the remaining equity to the win and loss sides
    p_win = w_exp_a * remaining_equity
    p_loss = w_exp_b * remaining_equity

    return p_win, p_draw, p_loss