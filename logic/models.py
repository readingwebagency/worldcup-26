from logic.elo import win_probability, update_elo


class Team:
    def __init__(self, name, rating, is_home=False):
        self.name = name
        self.rating = rating
        self.is_home = is_home

    def update_rating(self, k, w, we):
        self.rating = update_elo(self.rating, k, w, we)

    def __repr__(self):
        return f"Team({self.name}, {self.rating})"


class Group:
    def __init__(self, name, teams, fixtures):
        self.name = name
        self.teams = teams  # list of Team objects
        self.fixtures = fixtures  # list of dicts with home/away team names
        self.points = {team.name: 0 for team in teams}

    def update_points(self, team_a, team_b, outcome):
        if outcome == "home":
            self.points[team_a.name] += 3
        elif outcome == "away":
            self.points[team_b.name] += 3
        else:  # draw
            self.points[team_a.name] += 1
            self.points[team_b.name] += 1

    def standings(self):
        return sorted(self.teams, key=lambda t: self.points[t.name], reverse=True)

    def qualifiers(self):
        return self.standings()[:2]

    def __repr__(self):
        return f"Group({self.name}, {[t.name for t in self.teams]})"