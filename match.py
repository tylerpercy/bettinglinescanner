class match:

    home_team_id: str
    home_spread: str
    away_team_id: str
    away_spread: str
    total: float

    def __init__(self, homeTeamId, homeSpread, awayTeamId, awaySpread, total):
        self.home_team_id = homeTeamId
        self.home_spread = homeSpread
        self.away_team_id = awayTeamId
        self.away_spread = awaySpread
        self.total = total

    def __str__(self):
        return (
            "```"
            f"Away Team: {self.away_team_id} ({self.away_spread})\n"
            f"Home Team: {self.home_team_id} ({self.home_spread})\n"
            f"Total: {self.total}\n"
            "```"
        )
    
def build_match_list(betting_lines, team_ids):

    matches = []

    grouped_lines = [betting_lines[i:i+4][:-1] for i in range(0, len(betting_lines), 4)]
    grouped_teams = [team_ids[i:i+2] for i in range(0, len(team_ids), 2)]

    for lines, teams in zip(grouped_lines, grouped_teams):
        matches.append(match(teams[1], lines[2], teams[0], lines[0], lines[1]))

    return matches