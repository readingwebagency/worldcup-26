import json
from logic.match import simulate_match
from logic.models import Team, Group

# =====================================================================
# THE SIMULATION FUNCTION (Accepts objects directly)
# =====================================================================
def simulate_group_stage(group_obj, teams_lookup):
    """
    Simulates all scheduled fixtures for a given Group object.
    Mutates group points and dynamic team Elo ratings directly.
    """
    print(f"--- Simulating Group {group_obj.name} Matches ---")
    
    for match in group_obj.fixtures:
        home_team = teams_lookup[match['home']]
        away_team = teams_lookup[match['away']]
        
        # Simulate the match using current Elo ratings
        result = simulate_match(home_team.name, home_team.rating, away_team.name, away_team.rating)
        print(f"  {home_team.name} vs {away_team.name} -> Winner: {result['winner']}")
        
        # Update points table using the matched team/winner names
        group_obj.update_points(home_team, away_team, result['winner'])
        
        # Mutate the actual Elo ratings on the team objects for subsequent games
        home_team.rating = result['new_ratings'][home_team.name]
        away_team.rating = result['new_ratings'][away_team.name]


# =====================================================================
# OBJECT INSTANTIATION STEP
# =====================================================================
if __name__ == "__main__":
    # Load JSON source files from the data/ directory
    with open('data/teams.json', 'r') as f: teams_data = json.load(f)
    with open('data/groups.json', 'r') as f: groups_data = json.load(f)
    with open('data/fixtures.json', 'r') as f: fixtures_data = json.load(f)

    # 1. Instantiate ALL Team objects into a reference dictionary
    all_teams = {}
    for t in teams_data:
        all_teams[t['name']] = Team(name=t['name'], rating=t['rating'], is_home=t['isHome'])

    # 2. Pick a target group configuration (e.g., Group "A")
    target_letter = "A"
    group_cfg = next(g for g in groups_data if g['name'] == target_letter)
    
    # 3. Collect the specific Team instances belonging to Group A
    group_teams_objects = [all_teams[name] for name in group_cfg['teams']]
    
    # 4. Filter out the fixtures assigned to Group A
    group_fixtures_list = [f for f in fixtures_data if f['group'] == target_letter]

    # 5. Instantiate the Group object explicitly
    group_a_object = Group(name=target_letter, teams=group_teams_objects, fixtures=group_fixtures_list)

    # =====================================================================
    # SIMULATION CALL
    # =====================================================================
    # Pass your pre-built Group object and Team dictionary lookup straight in!
    simulate_group_stage(group_a_object, all_teams)

    # Output the results using the methods defined inside your Group class
    print(f"\n--- Final Standings for Group {group_a_object.name} ---")
    for rank, team in enumerate(group_a_object.standings(), start=1):
        points = group_a_object.points[team.name]
        print(f"  {rank}. {team.name:<15} Points: {points} (Ending Elo: {int(team.rating)})")
        
    print(f"\nQualifiers progressing to Knockouts: {[t.name for t in group_a_object.qualifiers()]}")