import argparse
from datetime import datetime
from logic.generate_data import generate_lookup_json
from logic.groups import (
    get_group_fixture_probabilities,
    simulate_single_group_stage,
    calculate_group_position_matrix,
    simulate_full_tournament_n_times,
    simulate_world_champion_probabilities,
    simulate_group_stage_and_show_wildcards
)

# ==============================================================================
# CLI HANDLER FUNCTIONS
# ==============================================================================

def handle_generate(args):
    """Handler executed when running: python main.py generate"""
    generate_lookup_json()


def print_fixtures(title, fixtures_probs):
    """Helper utility to cleanly format and display match probabilities in terminal."""
    print("=============================================")
    print(f"     {title}     ")
    print("=============================================\n")
    
    for match in fixtures_probs:
        date_obj = datetime.strptime(match["date"], "%Y-%m-%d")
        formatted_date = date_obj.strftime("%B %d, %Y")
        
        print(f"📅 {formatted_date}")
        print(f"   {match['home']} (Home) vs. {match['away']} (Away)")
        print(f"   └─ {match['home']} Win: {match['p_home_win'] * 100:.1f}% | Draw: {match['p_draw'] * 100:.1f}% | {match['away']} Win: {match['p_away_win'] * 100:.1f}%")
        print("-" * 50)


def handle_group(args):
    """Handler executed when running: python main.py group [LETTER]"""
    letter = args.letter.upper()
    fixtures_probs = get_group_fixture_probabilities(letter)
    
    if not fixtures_probs:
        print(f"❌ Error: No upcoming fixtures found for Group {letter}.")
        return
        
    print_fixtures(f"GROUP {letter} MATCH PROBABILITIES", fixtures_probs)


def handle_all(args):
    """Handler executed when running: python main.py all"""
    for letter in ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L"]:
        fixtures_probs = get_group_fixture_probabilities(letter)
        if fixtures_probs:
            print_fixtures(f"GROUP {letter} MATCH PROBABILITIES", fixtures_probs)


def handle_simulate(args):
    """Handler executed when running: python main.py simulate [LETTER]"""
    letter = args.letter.upper()
    
    if args.matrix:
        print(f"📊 Calculating Final Standings Distribution Matrix for Group {letter} ({args.iterations:,} runs)...")
        try:
            matrix = calculate_group_position_matrix(letter, iterations=args.iterations)
            
            print("\n=======================================================")
            print(f"     GROUP {letter} POSITION PROBABILITY MATRIX         ")
            print("=======================================================")
            print(f"{'Team':<20} | {'1st':<7} | {'2nd':<7} | {'3rd':<7} | {'4th':<7}")
            print("-" * 55)
            
            for team, positions in matrix.items():
                print(f"{team:<20} | {positions[1]:>5.1f}% | {positions[2]:>5.1f}% | {positions[3]:>5.1f}% | {positions[4]:>5.1f}%")
            print("=======================================================\n")
        except ValueError as e:
            print(f"❌ {e}")
            
    else:
        # Load data dynamically inside execution block to isolate single run tracking
        from logic.groups import load_simulation_data
        try:
            groups, all_fixtures, lookup_table, teams_elo = load_simulation_data(
                "data/groups.json", "data/fixtures.json", "data/lookup_table.json", "data/teams.json"
            )
            target_group = next((g for g in groups if g["name"].upper() == letter), None)
            if not target_group:
                print(f"❌ Error: Group '{letter}' not found.")
                return
                
            group_fixtures = [m for m in all_fixtures if m["group"].upper() == letter]
            
            # Execute a single group run unpacking our 3-element return values: (team, points, gd)
            standings = simulate_single_group_stage(target_group["teams"], group_fixtures, lookup_table, teams_elo)
            
            print(f"\n🏁 Final Group {letter} Standings (GD Proxy Heuristic):")
            print(f"{'Pos':<4} | {'Team':<20} | {'Points':<6} | {'GD':<4}")
            print("-" * 43)
            for idx, (team, pts, gd) in enumerate(standings):
                print(f"{idx+1:<4} | {team:<20} | {pts:<6} | {gd:<+4}")
            print("-" * 43)
        except FileNotFoundError:
            print("❌ Error: Missing data dependencies in the data/ directory.")


def handle_wildcards(args):
    """Handler executed when running: python main.py wildcards"""
    simulate_group_stage_and_show_wildcards()

def handle_round_of_32(args):
    """Handler executed when running: python main.py roundof32"""
    import json
    results = simulate_full_tournament_n_times(iterations=args.iterations)
    
    # Load groups data to organize our flat results dictionary alphabetically by group name
    try:
        with open("data/groups.json", 'r') as f:
            groups_data = json.load(f)
    except FileNotFoundError:
        print("❌ Error: data/groups.json not found. Cannot sort output by group structure.")
        return

    print("\n=======================================================")
    print("     PROBABILITY TO ADVANCE TO THE ROUND OF 32       ")
    print("=======================================================")
    
    # Sort groups alphabetically by their group name (e.g., Group A, Group B...)
    sorted_groups = sorted(groups_data, key=lambda g: g["name"].upper())
    
    for group in sorted_groups:
        group_letter = group["name"].upper()
        print(f"\n🟩 GROUP {group_letter}:")
        print("-" * 35)
        
        # Pull the teams belonging to this specific group and pair them with their results
        group_teams_probs = {team: results.get(team, 0.0) for team in group["teams"]}
        
        # Sort the teams inside this group block by their advancement odds descending
        sorted_teams = sorted(group_teams_probs.items(), key=lambda x: x[1], reverse=True)
        
        for team, prob in sorted_teams:
            print(f"  ⚽ {team:<20} -> {prob:>5.1f}%")
            
    print("\n=======================================================\n")


def handle_champion(args):
    """Handler executed when running: python main.py champion"""
    champ_odds = simulate_world_champion_probabilities(iterations=args.iterations)
    
    print("\n=======================================================")
    print("           PROJECTED WORLD CHAMPION ODDS               ")
    print("=======================================================")
    print(f"{'Rank':<5} | {'Team':<22} | {'Win %':<8}")
    print("-" * 42)
    
    # Transform dictionary items into sorted list for rank output
    sorted_champs = sorted(champ_odds.items(), key=lambda x: x[1], reverse=True)
    for rank, (team, prob) in enumerate(sorted_champs):
        print(f"#{rank+1:<4} | {team:<22} | {prob:>5.2f}%")
        
    print("=======================================================\n")

def handle_tournament_matrix(args):
    """Handler executed when running: python main.py matrix"""
    from logic.groups import calculate_full_tournament_matrix
    
    results = calculate_full_tournament_matrix(iterations=args.iterations)
    
    # Sort teams by championship odds descending, then final odds, then L32 odds
    sorted_teams = sorted(
        results.items(), 
        key=lambda x: (x[1]["CHAMPION"], x[1]["FINAL"], x[1]["SF"], x[1]["L32"]), 
        reverse=True
    )
    
    print("\n=========================================================================================")
    print("                      GLOBAL TOURNAMENT PROGRESSION PROBABILITY MATRIX                     ")
    print("=========================================================================================")
    print(f"{'Team':<22} | {'Top Grp':<7} | {'L32':<7} | {'L16':<7} | {'QF':<7} | {'SF':<7} | {'Final':<7} | {'Champ':<7}")
    print("-" * 89)
    
    for team, stages in sorted_teams:
        print(f"{team:<22} | "
              f"{stages['Top Group']:>6.1f}% | "
              f"{stages['L32']:>6.1f}% | "
              f"{stages['L16']:>6.1f}% | "
              f"{stages['QF']:>6.1f}% | "
              f"{stages['SF']:>6.1f}% | "
              f"{stages['FINAL']:>6.1f}% | "
              f"{stages['CHAMPION']:>6.1f}%")
              
    print("=========================================================================================\n")

def handle_top_6_distribution(args):
    """Handler executed when running: python main.py distribution"""
    # Import the function from groups.py (assuming logic/groups.py or wherever groups.py sits)
    # Adjust this import path if your file structure is different!
    from logic.groups import analyze_top_6_semifinal_distribution
    
    # Run the simulation with paths defined in your environment or fallbacks
    analyze_top_6_semifinal_distribution(
        iterations=args.iterations,
        groups_path="data/groups.json",
        fixtures_path="data/fixtures.json",
        lookup_path="data/lookup_table.json",
        teams_path="data/teams.json"
    )


# ==============================================================================
# MAIN ROUTINE RUNNER (ARGPARSE SUBCOMMAND TREE INTERFACE)
# ==============================================================================

def main():
    parser = argparse.ArgumentParser(description="World Cup 2026 Simulation & Metrics Toolkit Suite Engine")
    subparsers = parser.add_subparsers(dest="command", help="Subcommands")

    # Command: generate
    parser_gen = subparsers.add_parser("generate", help="Build and compile data lookup JSON file matrix matrices profiles")
    parser_gen.set_defaults(func=handle_generate)

    # Command: group
    parser_group = subparsers.add_parser("group", help="Display fixture statistics probabilities for a singular specific group layout configuration")
    parser_group.add_argument("letter", type=str, help="The target letter (e.g. A, B, C etc.)")
    parser_group.set_defaults(func=handle_group)

    # Command: all
    parser_all = subparsers.add_parser("all", help="Parse and process fixture tables across structural profiles for all groups sequentially")
    parser_all.set_defaults(func=handle_all)

    # Command: simulate
    parser_simulate = subparsers.add_parser("simulate", help="Run simulation iterations for a group")
    parser_simulate.add_argument("letter", type=str, help="The target group letter to simulate (e.g. A, B, C)")
    parser_simulate.add_argument("--matrix", action="store_true", help="Calculate position probability distributions matrix")
    parser_simulate.add_argument("--iterations", type=int, default=10000, help="Number of matrix iterations to run (default: 10,000)")
    parser_simulate.set_defaults(func=handle_simulate)

    # Command: wildcards
    parser_wildcards = subparsers.add_parser("wildcards", help="Simulate a group stage iteration and print the 3rd place rankings pool")
    parser_wildcards.set_defaults(func=handle_wildcards)

    # Command: roundof32
    parser_r32 = subparsers.add_parser("roundof32", help="Calculate Round of 32 advancement odds for all teams")
    parser_r32.add_argument("--iterations", type=int, default=5000, help="Number of brackets to test (default: 5,000)")
    parser_r32.set_defaults(func=handle_round_of_32)

    # Command: champion
    parser_champion = subparsers.add_parser("champion", help="Simulate the entire tournament to find title probabilities")
    parser_champion.add_argument("--iterations", type=int, default=5000, help="Number of global tournaments to test (default: 5,000)")
    parser_champion.set_defaults(func=handle_champion)

    # Command: matrix
    parser_matrix = subparsers.add_parser("matrix", help="Calculate full stage-by-stage progression probabilities for all teams")
    parser_matrix.add_argument("--iterations", type=int, default=5000, help="Number of full tournaments to run (default: 5,000)")
    parser_matrix.set_defaults(func=handle_tournament_matrix)

    # Command: distribution
    parser_dist = subparsers.add_parser(
        "distribution", 
        help="Calculate exact probability distribution of top-6 teams reaching the Semi-Finals"
    )
    parser_dist.add_argument(
        "--iterations", 
        type=int, 
        default=5000, 
        help="Number of global brackets to run (default: 5,000)"
    )
    parser_dist.set_defaults(func=handle_top_6_distribution)

    # Parse arguments and map to default actions
    args = parser.parse_args()
    if hasattr(args, 'func'):
        args.func(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()