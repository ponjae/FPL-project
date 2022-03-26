import requests


class gameData:

    def __init__(self):

        response = requests.get(
            "https://fantasy.premierleague.com/api/bootstrap-static/")
        data = response.json()
        self.gw_data = self._load_gameweek_data(data)
        self.pl_table = self._load_pl_table(data)
        self.fixture_data = self._load_fixture_data()
        self.team_data_dict = self._load_team_data()

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

    def _load_team_data(self):
        """
        Metod for providing information about each team in the league. Will be used in the team-page.

        Returns:
            dict: dict containing all teams and their respective information
        """

        team_data_dict = {
            "Arsenal": {
                "name": "The Arsenal Football Club",
                "nickname": "The Gunners",
                "city": "London",
                "arena": "Emirates Stadium",
                "coach": "Mikel Arteta",
                "pl-titles": "13"
            },
            "AstonVilla": {
                "name": "Aston Villa Football Club",
                "nickname": "The Villans",
                "city": "Birmingham",
                "arena": "Villa Park",
                "coach": "Steven Gerrard",
                "pl-titles": "7"
            },
            "Brentford": {
                "name": "Brentford Football Club",
                "nickname": "The Bees",
                "city": "London",
                "arena": "Brentford Community Stadium",
                "coach": "Thomas Frank",
                "pl-titles": "0"
            },
            "Brighton": {
                "name": "Brighton & Hove Albion Football Club",
                "nickname": "The Seagulls",
                "city": "Brighton",
                "arena": "Falmer Stadium",
                "coach": "Graham Potter",
                "pl-titles": "0"
            },
            "Burnley": {
                "name": "Burnley Football Club",
                "nickname": "The Clarets",
                "city": "Burnley",
                "arena": "Turf Moor",
                "coach": "Sean Dyche",
                "pl-titles": "2"
            },
            "Chelsea": {
                "name": "Chelsea Football Club",
                "nickname": "The Blues",
                "city": "London",
                "arena": "Stamford Bridge",
                "coach": "Thomas Tuchel",
                "pl-titles": "6"
            },
            "CrystalPalace": {
                "name": "Crystal Palace Football Club",
                "nickname": "The Eagles",
                "city": "London",
                "arena": "Selhurst Park",
                "coach": "Patrick Vieira",
                "pl-titles": "0"
            },
            "Everton": {
                "name": "Everton Football Club",
                "nickname": "The Toffees",
                "city": "Liverpool",
                "arena": "Goodison Park",
                "coach": "Frank Lampard",
                "pl-titles": "9"
            },
            "Leicester": {
                "name": "Leicester City Football Club",
                "nickname": "The Foxes",
                "city": "Leicester",
                "arena": "King Power Stadium",
                "coach": "Brendan Rodgers",
                "pl-titles": "1"
            },
            "Leeds": {
                "name": "Leeds United Football Club",
                "nickname": "The Peacooks",
                "city": "Leeds",
                "arena": "Elland Road",
                "coach": "Jesse Marsch",
                "pl-titles": "3"
            },
            "Liverpool": {
                "name": "Liverpool Football Club",
                "nickname": "The Reds",
                "city": "Liverpool",
                "arena": "Anfield",
                "coach": "Jürgen Klopp",
                "pl-titles": "19"
            },
            "ManCity": {
                "name": "Manchester City Football Club",
                "nickname": "City",
                "city": "Manchester",
                "arena": "Etihad Stadium",
                "coach": "Pep Guardiola",
                "pl-titles": "7"
            },
            "ManUtd": {
                "name": "Manchester United Football Club",
                "nickname": "The Red Devils",
                "city": "Manchester",
                "arena": "Old Trafford",
                "coach": "Ralf Rangnick",
                "pl-titles": "20"
            },
            "Newcastle": {
                "name": "Newcastle United Football Club",
                "nickname": "The Magpies",
                "city": "Newcastle",
                "arena": "St James' Park",
                "coach": "Eddie Howe",
                "pl-titles": "4"
            },
            "Norwich": {
                "name": "Norwich City Football Club",
                "nickname": "The Canaries",
                "city": "Norwich",
                "arena": "Carrow Road",
                "coach": "Dean Smith",
                "pl-titles": "0"
            },
            "Southampton": {
                "name": "Southampton Football Club",
                "nickname": "The Saints",
                "city": "Southampton",
                "arena": "St Mary's Stadium",
                "coach": "Ralph Hasenhüttl",
                "pl-titles": "0"
            },
            "Spurs": {
                "name": "Tottenham Hotspur Football Club",
                "nickname": "Spurs",
                "city": "London",
                "arena": "Tottenham Hotspur Stadium",
                "coach": "Antonio Conte",
                "pl-titles": "2"
            },
            "Watford": {
                "name": "Watford Football Club",
                "nickname": "The Hornets",
                "city": "Watford",
                "arena": "Vicarage Road",
                "coach": "Roy Hodgson",
                "pl-titles": "0"
            },
            "WestHam": {
                "name": "West Ham United Football Club",
                "nickname": "The Irons",
                "city": "London",
                "arena": "London Stadium",
                "coach": "David Moyes",
                "pl-titles": "0"
            },
            "Wolves": {
                "name": "Wolverhampton Wanderers Football Club",
                "nickname": "Wolves",
                "city": "Wolverhampton",
                "arena": "Molineux Stadium",
                "coach": "Bruno Lage",
                "pl-titles": "3"
            }
        }

        return team_data_dict
