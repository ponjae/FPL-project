import requests


class gameData:

    def __init__(self):

        response = requests.get(
            "https://fantasy.premierleague.com/api/bootstrap-static/")
        data = response.json()
        self.gw_data = self._load_gameweek_data(data)
        self.pl_table = self._load_pl_table(data)
        self.fixture_data = self._load_fixture_data()

    def _load_gameweek_data(self, data):
        """ Method for fetching the gameweek data to be displayed on the home page

        Args:
            data (dict): the relevant api-data

        Returns:
            dict: A dict containing information about every gameweek

        """

        gw_data_dict = {}

        for gw_nbr, gw_data in enumerate(data["events"]):
            self._populate_gw_dict(gw_nbr + 1, gw_data, gw_data_dict)

        return gw_data_dict

    def _load_pl_table(self, data):
        """ Constructs a table dict of teams from the league (seems to not be working)

        Args:
            data (dict): the relevant api-data

        Returns:
            dict: a dict containing the table position as keys and team data as values
        """

        table_dict = {}

        for team_data in data["teams"]:
            club = team_data["name"]
            played = team_data["played"]
            wins = team_data["win"]
            draws = team_data["draw"]
            losses = team_data["loss"]
            points = team_data["points"]
            position = team_data["code"]
            table_dict[position] = (club, played, wins, draws, losses, points)

        return table_dict

    def _populate_gw_dict(self, gw_number, gw, storage):
        """ Helper method for filtering out the relevant information from the gw and storing it
        in the dict

        Args:
            gw_number (int): the gw number
            gw (dict): all available information about gw
            storage (dict): the dict to store the data in
        """
        wanted_keys = ["id", "average_entry_score", "finished",
                       "highest_score", "top_element_info", "most_captained"]

        storage[gw_number] = {}

        for key in gw.keys():
            if key in wanted_keys:
                storage[gw_number][key] = gw[key]
            elif key == "chip_plays":
                chip_data = gw[key]
                for chip in chip_data:
                    storage[gw_number][chip["chip_name"]] = chip["num_played"]

    def _load_fixture_data(self):
        """ Method for adding the games for each gameweek

        Returns:
            dict: The dict containin the games for each gw
        """
        response = requests.get(
            "https://fantasy.premierleague.com/api/fixtures/")
        data = response.json()

        fixtures = {}

        for game in data:
            home_team = game["team_h"]
            away_team = game["team_a"]
            gw_number = game["event"]
            home_score = game["team_h_score"]
            away_score = game["team_a_score"]
            finished = game["finished"]
            gw = game["event"]
            if gw_number in fixtures:
                fixtures[gw_number].append(
                    (finished, home_team, away_team, home_score, away_score, gw))
            else:
                fixtures[gw_number] = [
                    (finished, home_team, away_team, home_score, away_score, gw)]
        return fixtures

    def convert_fixtures(self, id_and_team_dict):
        """ Convert the fixtures to a readable format using the id
        and team dict from playerData

        Args:
            id_and_team_dict (dict): Dict containing the id and team names

        Returns:
            dict : dict containing the gw as key then a list with the games as values
        """

        current_gw = self._current_gw_number(self.fixture_data)
        readable_dict = {current_gw: []}

        for game in self.fixture_data[current_gw]:

            finished, ht, at, h_score, a_score, gw = game
            home_team = id_and_team_dict[ht]
            away_team = id_and_team_dict[at]
            readable_dict[gw].append(
                (finished, home_team, away_team, h_score, a_score, gw))
        return readable_dict

    def _current_gw_number(self, all_fixtures):

        # remove unscheduled games
        all_fixtures.pop(None, None)
        gws = sorted(all_fixtures.keys())

        current_gw = -1

        for gw in gws:
            for game in all_fixtures[gw]:
                if not game[0]:
                    current_gw = gw
                    break
            else:
                continue
            break

        return current_gw
