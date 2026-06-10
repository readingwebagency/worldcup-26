import json
from collections import Counter
import random
from logic.match import simulate_match

# ==============================================================================
# 1. CORE REUSABLE HELPER FUNCTIONS
# ==============================================================================

def load_simulation_data(groups_path, fixtures_path, lookup_path, teams_path=None):
    """
    Central helper that handles all file loading and string-to-tuple parsing 
    for lookup table mapping compatibility.
    """
    with open(groups_path, 'r') as f:
        groups = json.load(f)
    with open(fixtures_path, 'r') as f:
        fixtures = json.load(f)
    with open(lookup_path, 'r') as f:
        raw_lookup = json.load(f)
        lookup_table = {}
        for k, v in raw_lookup.items():
            t1, t2 = k.split(" vs ")
            lookup_table[(t1, t2)] = v

    teams_elo = {}
    if teams_path:
        with open(teams_path, 'r') as f:
            teams_elo = {t["name"]: t["rating"] for t in json.load(f)}
            
    return groups, fixtures, lookup_table, teams_elo


def get_group_fixtures(fixtures, group_letter):
    """
    Helper to filter and extract fixtures belonging to a specific group.
    """
    return [m for m in fixtures if m["group"].upper() == group_letter.upper()]


def rank_wildcards(third_place_pool):
    """
    Centralized sorting engine for the 3rd-place global wildcard pool.
    Sorts by Points, then Simulated GD, then a random tiebreaker.
    """
    return sorted(
        third_place_pool,
        key=lambda x: (x["points"], x["gd"], random.random()),
        reverse=True
    )


def simulate_single_group_stage(group_teams, group_fixtures, lookup_table, teams_elo):
    """
    Simulates matches for a single group and returns an ordered list of 
    team standings sorted by Points (Primary), Simulated GD (Secondary), and Elo (Tertiary).
    """
    points_table = {team: 0 for team in group_teams}
    gd_table = {team: 0 for team in group_teams}  # Track synthetic Goal Difference proxy
    
    for match in group_fixtures:
        res = simulate_match(match["home"], match["away"], lookup_table, is_knockout=False)
        
        # Accumulate Points
        points_table[match["home"]] += res["points"][0]
        points_table[match["away"]] += res["points"][1]
        
        # Accumulate Goal Difference
        gd_table[match["home"]] += res["gd"][0]
        gd_table[match["away"]] += res["gd"][1]
        
    # Python Timsort preserves order if keys match. We sort inversely on all metrics.
    sorted_standings = sorted(
        group_teams,
        key=lambda team: (points_table[team], gd_table[team], teams_elo.get(team, 0)),
        reverse=True
    )
    
    return [(team, points_table[team], gd_table[team]) for team in sorted_standings]


# ==============================================================================
# 2. CLI EXECUTABLE ENGINES
# ==============================================================================

def get_group_fixture_probabilities(group_letter, groups_path="data/groups.json", fixtures_path="data/fixtures.json", lookup_path="data/lookup_table.json"):
    """
    Looks up and displays raw probability data for a group's scheduled fixtures.
    """
    groups, fixtures, lookup_table, _ = load_simulation_data(groups_path, fixtures_path, lookup_path)
    
    target_group = next((g for g in groups if g["name"].upper() == group_letter.upper()), None)
    if not target_group:
        raise ValueError(f"Group '{group_letter}' not found in configuration files.")
        
    group_fixtures = get_group_fixtures(fixtures, group_letter)
    results = []
    
    for match in group_fixtures:
        team_a, team_b = sorted([match["home"], match["away"]])
        p_win_a, p_draw, p_win_b = lookup_table[(team_a, team_b)]
        
        results.append({
            "home": match["home"],
            "away": match["away"],
            "date": match["date"],
            "p_home_win": p_win_a if team_a == match["home"] else p_win_b,
            "p_draw": p_draw,
            "p_away_win": p_win_b if team_a == match["home"] else p_win_a
        })
    return results


def simulate_single_group_once(group_letter, groups_path="data/groups.json", fixtures_path="data/fixtures.json", lookup_path="data/lookup_table.json", teams_path="data/teams.json"):
    """
    Simulates a single group stage exactly once and returns the finalized standings list.
    """
    groups, fixtures, lookup_table, teams_elo = load_simulation_data(groups_path, fixtures_path, lookup_path, teams_path)
    
    target_group = next((g for g in groups if g["name"].upper() == group_letter.upper()), None)
    if not target_group:
        raise ValueError(f"Group '{group_letter}' not found.")
        
    group_fixtures = get_group_fixtures(fixtures, group_letter)
    return simulate_single_group_stage(target_group["teams"], group_fixtures, lookup_table, teams_elo)


def calculate_group_position_matrix(group_letter, iterations=10000, groups_path="data/groups.json", fixtures_path="data/fixtures.json", lookup_path="data/lookup_table.json", teams_path="data/teams.json"):
    """
    Calculates the position probability distributions matrix over N iterations for a group.
    """
    groups, fixtures, lookup_table, teams_elo = load_simulation_data(groups_path, fixtures_path, lookup_path, teams_path)
    
    target_group = next((g for g in groups if g["name"].upper() == group_letter.upper()), None)
    if not target_group:
        raise ValueError(f"Group '{group_letter}' not found.")
        
    group_teams = target_group["teams"]
    group_fixtures = get_group_fixtures(fixtures, group_letter)
    
    matrix = {team: {1: 0, 2: 0, 3: 0, 4: 0} for team in group_teams}
    
    for _ in range(iterations):
        standings = simulate_single_group_stage(group_teams, group_fixtures, lookup_table, teams_elo)
        for idx, (team, _, _) in enumerate(standings):
            matrix[team][idx + 1] += 1
            
    # Convert frequencies to percentages
    for team in matrix:
        for pos in matrix[team]:
            matrix[team][pos] = (matrix[team][pos] / iterations) * 100
            
    return matrix


# ==============================================================================
# 3. GLOBAL TOURNAMENT & KNOCKOUT BRACKET SIMULATION ENGINES
# ==============================================================================

def simulate_tournament_once_to_champion(groups_path, fixtures_path, lookup_table, teams_elo):
    """
    Runs an entirely localized tournament timeline simulation using realistic 
    FIFA 48-team knockout mapping grids up to a single winner.
    """
    with open(groups_path, 'r') as f:
        groups = json.load(f)
    with open(fixtures_path, 'r') as f:
        fixtures = json.load(f)
        
    winners = {}
    runners_up = {}
    third_place_pool = []
    
    # 1. Run the 12 Groups
    for group in groups:
        letter = group["name"].upper()
        group_fixtures = get_group_fixtures(fixtures, letter)
        
        standings = simulate_single_group_stage(group["teams"], group_fixtures, lookup_table, teams_elo)
        
        # Pull exact winners and runners up
        winners[letter] = standings[0][0]
        runners_up[letter] = standings[1][0]
        
        # Capture the 3rd place row data for wildcard sorting
        third_team, third_pts, third_gd = standings[2]
        third_place_pool.append({
            "team": third_team,
            "group": letter,
            "points": third_pts,
            "gd": third_gd
        })
        
    # 2. Sort global 3rd-place pool using centralized helper
    sorted_wildcards = rank_wildcards(third_place_pool)
    top_8_wildcards = sorted_wildcards[:8]
    
    # 3. Build the official Left-Side vs Right-Side Round of 32 Slots
    r32_teams = [None] * 32
    
    # --- LEFT SIDE BRACKET (Slots 0 to 15) ---
    r32_teams[0]  = winners["A"]
    r32_teams[1]  = runners_up["B"]
    r32_teams[2]  = winners["C"]
    r32_teams[3]  = runners_up["D"]
    r32_teams[4]  = winners["E"]
    r32_teams[5]  = runners_up["F"]
    r32_teams[6]  = winners["G"]
    r32_teams[7]  = runners_up["H"]
    r32_teams[8]  = winners["I"]
    r32_teams[9]  = runners_up["J"]
    r32_teams[10] = winners["K"]
    r32_teams[11] = runners_up["L"]
    
    # --- RIGHT SIDE BRACKET (Slots 16 to 31) ---
    r32_teams[16] = winners["B"]
    r32_teams[17] = runners_up["A"]
    r32_teams[18] = winners["D"]
    r32_teams[19] = runners_up["C"]
    r32_teams[20] = winners["F"]
    r32_teams[21] = runners_up["E"]
    r32_teams[22] = winners["H"]
    r32_teams[23] = runners_up["G"]
    r32_teams[24] = winners["J"]
    r32_teams[25] = runners_up["I"]
    r32_teams[26] = winners["L"]
    r32_teams[27] = runners_up["K"]
    
    # --- ALLOCATE THE 8 WILDCARDS DYNAMICALLY INTO THE REMAINING BLANK SLOTS ---
    left_wildcard_slots = [12, 13, 14, 15]
    right_wildcard_slots = [28, 29, 30, 31]
    
    for team_info in top_8_wildcards:
        team = team_info["team"]
        g_letter = team_info["group"]
        
        if g_letter in ["B", "D", "F", "H", "J", "L"] and left_wildcard_slots:
            slot = left_wildcard_slots.pop(0)
            r32_teams[slot] = team
        elif right_wildcard_slots:
            slot = right_wildcard_slots.pop(0)
            r32_teams[slot] = team
        else:
            slot = left_wildcard_slots.pop(0) if left_wildcard_slots else right_wildcard_slots.pop(0)
            r32_teams[slot] = team

    # 4. Run the Knockout Tournament Structure tree sequentially
    current_round_teams = r32_teams
    
    while len(current_round_teams) > 1:
        next_round_teams = []
        for i in range(0, len(current_round_teams), 2):
            t1 = current_round_teams[i]
            t2 = current_round_teams[i+1]
            
            res = simulate_match(t1, t2, lookup_table, is_knockout=True)
            next_round_teams.append(res["winner"])
            
        current_round_teams = next_round_teams
        
    return current_round_teams[0]


def simulate_full_tournament_n_times(iterations=5000, groups_path="data/groups.json", fixtures_path="data/fixtures.json", lookup_path="data/lookup_table.json", teams_path="data/teams.json"):
    """
    Runs tournament simulations to track Round of 32 advancement rates across all 48 teams.
    """
    groups, fixtures, lookup_table, teams_elo = load_simulation_data(groups_path, fixtures_path, lookup_path, teams_path)
    
    advancement_counts = {}
    for group in groups:
        for team in group["teams"]:
            advancement_counts[team] = 0
            
    print(f"📊 Simulating {iterations:,} full tournament group stages to map Round of 32 advancement...")
    
    for i in range(iterations):
        if (i + 1) % 1000 == 0:
            print(f"   ⏳ Completed {i + 1:,} simulations...")
            
        next_round_teams = []
        third_place_pool = []
        
        for group in groups:
            letter = group["name"].upper()
            group_fixtures = get_group_fixtures(fixtures, letter)
            
            standings = simulate_single_group_stage(group["teams"], group_fixtures, lookup_table, teams_elo)
            
            next_round_teams.append(standings[0][0])
            next_round_teams.append(standings[1][0])
            
            third_team, third_pts, third_gd = standings[2]
            third_place_pool.append({
                "team": third_team,
                "points": third_pts,
                "gd": third_gd
            })
            
        sorted_wildcards = rank_wildcards(third_place_pool)
        
        for wildcard in sorted_wildcards[:8]:
            next_round_teams.append(wildcard["team"])
            
        for qualified_team in next_round_teams:
            advancement_counts[qualified_team] += 1
            
    return {team: (count / iterations) * 100 for team, count in advancement_counts.items()}


def simulate_world_champion_probabilities(iterations=5000, groups_path="data/groups.json", fixtures_path="data/fixtures.json", lookup_path="data/lookup_table.json", teams_path="data/teams.json"):
    """
    Runs full Monte Carlo tournament loops to calculate the ultimate championship odds.
    """
    if "lookup_path.json" in lookup_path: 
        lookup_path = "data/lookup_table.json"
        
    groups, fixtures, lookup_table, teams_elo = load_simulation_data(groups_path, fixtures_path, lookup_path, teams_path)
        
    champion_counts = {}
    for group in groups:
        for team in group["teams"]:
            champion_counts[team] = 0
            
    print(f"🏆 Simulating {iterations:,} full tournament brackets to find the World Champion...")
    
    for i in range(iterations):
        if (i + 1) % 1000 == 0:
            print(f"   ⏳ Completed {i + 1:,} simulations...")
        champ = simulate_tournament_once_to_champion(groups_path, fixtures_path, lookup_table, teams_elo)
        champion_counts[champ] += 1
        
    return {team: (count / iterations) * 100 for team, count in champion_counts.items()}


def simulate_group_stage_and_show_wildcards(groups_path="data/groups.json", fixtures_path="data/fixtures.json", lookup_path="data/lookup_table.json", teams_path="data/teams.json"):
    """
    Subcommand feature: Simulates all groups exactly once, extracts the 3rd-place team,
    ranks them globally using our new Goal Difference proxy rules, and shows who advances.
    """
    groups, all_fixtures, lookup_table, teams_elo = load_simulation_data(groups_path, fixtures_path, lookup_path, teams_path)
    third_place_pool = []

    for group in groups:
        letter = group["name"].upper()
        fixtures = get_group_fixtures(all_fixtures, letter)
        standings = simulate_single_group_stage(group["teams"], fixtures, lookup_table, teams_elo)
        
        third_team, third_pts, third_gd = standings[2]
        third_place_pool.append({
            "team": third_team,
            "group": letter,
            "points": third_pts,
            "gd": third_gd
        })
        
    sorted_wildcards = rank_wildcards(third_place_pool)
    
    print("\n=========================================================================")
    print("            LIVE 3RD-PLACE WILDCARD LEADERBOARD (GD PROXY)               ")
    print("=========================================================================")
    print(f"{'Rank':<5} | {'Group':<5} | {'Team':<22} | {'Points':<6} | {'GD':<4} | {'Status':<12}")
    print("-" * 73)
    
    for rank_idx, entry in enumerate(sorted_wildcards):
        rank = rank_idx + 1
        status = "✅ ADVANCED" if rank <= 8 else "❌ ELIMINATED"
        print(f"#{rank:<4} | Group {entry['group']:<1} | {entry['team']:<22} | {entry['points']:<6} | {entry['gd']:<4} | {status:<12}")
        
    print("=========================================================================\n")

def calculate_full_tournament_matrix(iterations=5000, groups_path="data/groups.json", fixtures_path="data/fixtures.json", lookup_path="data/lookup_table.json", teams_path="data/teams.json"):
    """
    Runs full Monte Carlo tournament loops using the official 48-team FIFA 
    knockout bracket layout template. Tracks realistic progressive milestones.
    """
    groups, fixtures, lookup_table, teams_elo = load_simulation_data(groups_path, fixtures_path, lookup_path, teams_path)
    
    # Initialize matrix tracking for all 48 teams
    stages = ["Top Group", "L32", "L16", "QF", "SF", "FINAL", "CHAMPION"]
    matrix = {team: {stage: 0 for stage in stages} for group in groups for team in group["teams"]}
    
    print(f"🏆 Running {iterations:,} official FIFA tournament brackets to map all stage vectors...")
    
    for iteration in range(iterations):
        if (iteration + 1) % 1000 == 0:
            print(f"   ⏳ Completed {iteration + 1:,} simulations...")
            
        winners = {}
        runners_up = {}
        third_place_pool = []
        
        # 1. Simulate Group Stage
        for group in groups:
            letter = group["name"].upper()
            group_fixtures = get_group_fixtures(fixtures, letter)
            standings = simulate_single_group_stage(group["teams"], group_fixtures, lookup_table, teams_elo)
            
            # Record who won their group
            matrix[standings[0][0]]["Top Group"] += 1
            
            winners[letter] = standings[0][0]
            runners_up[letter] = standings[1][0]
            
            third_team, third_pts, third_gd = standings[2]
            third_place_pool.append({
                "team": third_team, 
                "group": letter, 
                "points": third_pts, 
                "gd": third_gd
            })
            
        # 2. Extract Top 8 Wildcards
        sorted_wildcards = rank_wildcards(third_place_pool)
        w = [item["team"] for item in sorted_wildcards[:8]]
        
        # 3. Construct the Rigid 32-Team Knockout Tree
        # Even indices (0, 2, 4...) play odd indices (1, 3, 5...).
        # Spaced symmetrically so Group Winners play Wildcards or opposite Runners-up.
        r32_teams = [
            winners["A"], w[0],             # Match 1: Winner A vs Wildcard 1
            winners["B"], runners_up["C"],   # Match 2: Winner B vs Runner-up C
            winners["C"], w[1],             # Match 3: Winner C vs Wildcard 2
            winners["D"], runners_up["A"],   # Match 4: Winner D vs Runner-up A
            winners["E"], w[2],             # Match 5: Winner E vs Wildcard 3
            winners["F"], runners_up["G"],   # Match 6: Winner F vs Runner-up G
            winners["G"], w[3],             # Match 7: Winner G vs Wildcard 4
            winners["H"], runners_up["E"],   # Match 8: Winner H vs Runner-up E
            
            winners["I"], w[4],             # Match 9: Winner I vs Wildcard 5
            winners["J"], runners_up["K"],   # Match 10: Winner J vs Runner-up K
            winners["K"], w[5],             # Match 11: Winner K vs Wildcard 6
            winners["L"], runners_up["I"],   # Match 12: Winner L vs Runner-up I
            winners["M"] if "M" in winners else runners_up["B"], w[6], # Match 13 (Accounts for potential extra groups)
            winners["N"] if "N" in winners else runners_up["D"], runners_up["F"], # Match 14
            runners_up["H"], w[7],           # Match 15: Runner-up H vs Wildcard 8
            runners_up["J"], runners_up["L"] # Match 16: Runner-up J vs Runner-up L
        ]
        
        # Strip out any edge case Nones if your setup uses exactly 12 groups (A-L)
        r32_teams = [t for t in r32_teams if t is not None]
        
        # Pad up to 32 if group count variation left empty slots
        while len(r32_teams) < 32:
            r32_teams.append(w[-1]) # Fallback placeholder safety net
            
        # Record all teams that successfully made it into the Round of 32
        for team in r32_teams:
            matrix[team]["L32"] += 1
            
        # 4. Knockout Stages Tree Progression
        current_round = r32_teams
        ko_progressions = [
            ("L32_matches", "L16"),
            ("L16_matches", "QF"),
            ("QF_matches",  "SF"),
            ("SF_matches",  "FINAL"),
            ("FINAL_match", "CHAMPION")
        ]
        
        for round_name, milestone in ko_progressions:
            next_round = []
            for i in range(0, len(current_round), 2):
                t1, t2 = current_round[i], current_round[i+1]
                
                # Simulate core game match results
                res = simulate_match(t1, t2, lookup_table, is_knockout=True)
                
                # CHAOS VARIABLE: If the simulator returns a draw in knockouts, 
                # introduce the 50/50 penalty shootout lottery to nerf heavyweights.
                if res.get("outcome") == "draw" or res["winner"] is None:
                    winner = random.choice([t1, t2])
                else:
                    winner = res["winner"]
                    
                next_round.append(winner)
                
                # Milestone awarded ONLY to the team that won and advanced!
                matrix[winner][milestone] += 1
                
            current_round = next_round

    # Convert absolute counts to final baseline percentages
    for team in matrix:
        for stage in stages:
            matrix[team][stage] = (matrix[team][stage] / iterations) * 100
            
    return matrix