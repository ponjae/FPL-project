import requests


class fplData:

    def __init__(self):
        response = requests.get(
            'https://fantasy.premierleague.com/api/bootstrap-static/')
        raw_data = response.json()
        self.team_dict = self._get_teams(raw_data)
        self.arsenal = self._populate_team_dict(response.json())

    def _populate_team_dict(self, raw_data):
        team_dict = []
        player_data = raw_data['elements']
        for player in player_data:
            if player["team"] == 1:
                team_dict.append(player["second_name"])
        return sorted(team_dict)

    def _get_teams(self, raw_data):
        team_dict = {}
        for team in raw_data["teams"]:
            id_number = team["id"]
            team_name = team["name"]
            team_dict[id_number] = team_name
        return team_dict


for k, v in fplData().team_dict.items():
    print(f"Team: {v}, id: {k}")
