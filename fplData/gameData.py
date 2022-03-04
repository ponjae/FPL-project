import requests


class gameData:

    def __init__(self):
        self.gw_data = self.load_gameweek_data()
        self.fixture_data = self.load_fixture_data()

    def load_gameweek_data(self):
        """ Method for fetching the gameweek data to be displayed on the home page

        Returns:
            dict: A dict containing information about every gameweek
        """
        gw_data_dict = {}
        response = requests.get(
            "https://fantasy.premierleague.com/api/bootstrap-static/")
        data = response.json()

        for gw_nbr, gw_data in enumerate(data["events"]):
            self._populate_gw_dict(gw_nbr + 1, gw_data, gw_data_dict)

        return gw_data_dict

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

    def load_fixture_data(self):
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
                fixtures[gw_number] = []
        return fixtures

    def convert_fixtures(self, id_and_team_dict):
        """ Convert the fixtures to a readable format using the id
        and team dict from playerData

        Args:
            id_and_team_dict (dict): Dict containing the id and team names

        Returns:
            dict : dict containing the gw as key then a list with the games as values
        """
        readable_dict = {}

        for gw in self.fixture_data:
            if gw is not None:
                readable_dict[gw] = []
                for finished, ht, at, h_score, a_score, gw in self.fixture_data[gw]:
                    home_team = id_and_team_dict[ht]
                    away_team = id_and_team_dict[at]
                    readable_dict[gw].append(
                        (finished, home_team, away_team, h_score, a_score, gw))
        return readable_dict
