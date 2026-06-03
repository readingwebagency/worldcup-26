import math

# --- Your Constrained Cubic Configuration ---
MAX_DRAW = 0.28  # Peak draw rate when Elo difference is 0
C_PARAM = 0.15   # Controls the skew/tail behavior of the cubic curve
SCALE = 600      # Normalization factor for Elo differences

def win_probability(ri, rj):
    dr = ri - rj
    return 1 / (10 ** (-dr / 400) + 1)

def get_draw_rate(ri, rj):
    # Ensure symmetry by using absolute Elo difference
    diff = abs(ri - rj)
    x = diff / SCALE
    
    # If teams are so far apart that x > 1, floor the draw rate safely to 0
    if x >= 1.0:
        return 0.0
        
    p_draw = MAX_DRAW * (1 - x**2) + C_PARAM * (x**2 - x**3)
    return max(0.0, p_draw)  # Guard against any negative edge cases

def outcome_probs(ri, rj):
    w_exp = win_probability(ri, rj)
    p_draw = get_draw_rate(ri, rj)
    
    # Distribute remaining probabilities safely
    p_win = max(0.0, w_exp - (0.5 * p_draw))
    p_loss = max(0.0, (1 - w_exp) - (0.5 * p_draw))
    
    # Re-normalize to exactly 1.0 to ensure zero rounding errors
    total = p_win + p_draw + p_loss
    return p_win / total, p_draw / total, p_loss / total