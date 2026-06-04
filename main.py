import argparse
from datetime import datetime
from logic.groups import get_group_fixture_probabilities
from logic.generate_data import generate_lookup_json

def handle_generate(args):
    """Handler executed when running: python main.py generate"""
    generate_lookup_json()

def print_fixtures(title, fixtures_probs):
    """Helper utility to cleanly format and display match probabilities in the terminal."""
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
    group_letter = args.letter.upper()
    fixtures_probs = get_group_fixture_probabilities(group_letter)
    
    if not fixtures_probs:
        print(f"❌ Error: No fixtures data or matching group found for Group '{group_letter}'")
        return
        
    print_fixtures(f"CHRONOLOGICAL PROBABILITIES: GROUP {group_letter}", fixtures_probs)

def handle_all(args):
    """Handler executed when running: python main.py all"""
    # Loops through all tournament groups sequentially
    for letter in ["A", "B", "C", "D", "E", "F"]:
        fixtures_probs = get_group_fixture_probabilities(letter)
        if fixtures_probs:
            print_fixtures(f"CHRONOLOGICAL PROBABILITIES: GROUP {letter}", fixtures_probs)
            print("\n") # Line spacing between blocks

def handle_simulate(args):
    """Handler executed when running: python main.py simulate"""
    print("🏆 Initializing Tournament Simulation Engine...")
    print("🎲 Setting up Monte Carlo iterations... (Placeholder for future matching simulator code)")

def main():
    parser = argparse.ArgumentParser(
        description="Tournament Prediction & Monte Carlo Simulation Engine"
    )
    subparsers = parser.add_subparsers(dest="command", required=True, help="Available subcommands")

    # Command: group
    parser_group = subparsers.add_parser("group", help="Display fixture probabilities for a specific group")
    parser_group.add_argument("letter", type=str, help="The target group letter (e.g. A, B, C)")
    parser_group.set_defaults(func=handle_group)

    # Command: all
    parser_all = subparsers.add_parser("all", help="Display fixture probabilities for all groups sequentially")
    parser_all.set_defaults(func=handle_all)

    # Command: simulate
    parser_simulate = subparsers.add_parser("simulate", help="Run simulation iterations for the entire tournament bracket")
    parser_simulate.set_defaults(func=handle_simulate)

    # Commange: generate
    parser_generate = subparsers.add_parser("generate", help="Pre-compute and save the static Elo probability matrix")
    parser_generate.set_defaults(func=handle_generate)

    # Parse and execute routed command function
    args = parser.parse_args()
    args.func(args)

if __name__ == "__main__":
    main()