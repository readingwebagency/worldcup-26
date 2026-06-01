import random
from logic.elo import outcome_probs, update_elo

def simulate_match(team_a, ri, team_b, rj, draw_rate=0.28, k=40):
    p_win, p_draw, p_loss = outcome_probs(ri, rj, draw_rate)
    r = random.random()

    if r < p_win:
        w_a, w_b = 1, 0
    elif r < p_win + p_draw:
        w_a, w_b = 0.5, 0.5
    else:
        w_a, w_b = 0, 1

    #taken from eloratings.net/about
    we_a = p_win + (0.5 * p_draw)
    new_ri = update_elo(ri, k, w_a, we_a)
    new_rj = update_elo(rj, k, w_b, 1 - we_a)

    return {
        "winner": team_a if w_a == 1 else (team_b if w_b == 1 else "draw"),
        "scores": (w_a, w_b),
        "new_ratings": {team_a: new_ri, team_b: new_rj}
    }