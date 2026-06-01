import math

def win_probability(ri, rj):
    dr = ri - rj
    return 1 / (10 ** (-dr / 400) + 1)

def outcome_probs(ri, rj, p_draw):
    w_exp = win_probability(ri, rj)
    
    p_win = w_exp - (0.5 * p_draw)
    p_loss = (1 - w_exp) - (0.5 * p_draw)

    return p_win, p_draw, p_loss

def update_elo(ro, k, w, we):
    return ro + k * (w - we)