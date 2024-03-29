from distutils.log import error
import pulp
import pandas as pd


class playerRanking:

    def _sort_players_on_attribute(self, attribute, player_list):
        """ Method for merge sorting the players based on a specific attribute

        Args:
            attribute (String): the attribute that should be sort on
            player_list (list): the list to be sorted

        """

        if len(player_list) > 1:
            mid = len(player_list) // 2
            left = player_list[:mid]
            right = player_list[mid:]

            self._sort_players_on_attribute(attribute, left)
            self._sort_players_on_attribute(attribute, right)

            # Half iterators
            i = 0
            j = 0

            # Main list iterator
            m = 0

            while i < len(left) and j < len(right):
                if left[i][attribute] <= right[j][attribute]:
                    player_list[m] = left[i]
                    i += 1
                else:
                    player_list[m] = right[j]
                    j += 1
                m += 1

            while i < len(left):
                player_list[m] = left[i]
                i += 1
                m += 1

            while j < len(right):
                player_list[m] = right[j]
                j += 1
                m += 1

    def get_most_valuable_list(self, attribute, players, nbr, desc=True):
        """ Returns the most valueable players depending on attribute.

        Args:
            attribute (string): the attribute in which to rank the players
            players (dict): the players from which the most valueable should be found
            nbr (int): how many players to return
        Returns:
            list: A list of with the most valueable players
        """

        if attribute == "selected_by_percent":
            players = sorted(players, key=lambda x: float(x[attribute]))
        else:
            self._sort_players_on_attribute(attribute, players)

        # Desc ordering
        if desc:
            players = players[::-1]
        assert nbr <= len(players)

        return players[:nbr]

    def under_performers(self, team, horizon):
        """ Given a team return a list of player_values in ascending order in order
        to get an overview of the worst players in your team.

        Args:
            team (list): list of players
            horizon (int): how many weeks to consider
        Return:
            list: sorted list of players from team
        """
        to_consider_dict = {
            1: "PLAYER_VALUE",
            2: "total_points",
            5: "PLAYER_5_VALUE",
            10: "PLAYER_REMAINING_VALUE"
        }

        self._sort_players_on_attribute(to_consider_dict[horizon], team)
        return team

    def transfer_suggestion(self, transfer_out_id, all_players, itb, adjust_transfer_price=0.0):
        """ Given a player that you want to tranfer out, return a list with the best
        replacements for that player given your budget.

        Args:
            transfer_out_id (String): id of the player to transfer out
            all_players (dict): all players in the game
            itb (float): money in the bank
            adjust_transfer_price (float, Optional): adjusting the transfer price is now cost > return cost. Defaults to 0.
        Returns:
            (list): Transfer-suggestions for a given player
        """
        unwanted_player = all_players[transfer_out_id]
        position = unwanted_player["element_type"]
        total_budget = itb + \
            unwanted_player["now_cost"] + adjust_transfer_price

        best_alternatives_ids = [player for player in all_players if all_players[player]["element_type"]
                                 == position and all_players[player]["now_cost"] <= total_budget]

        # remove unwanted player
        best_alternatives_ids = list(filter(lambda player: (
            all_players[player]["id"] != transfer_out_id), best_alternatives_ids))

        best_alternatives = [player for player in all_players.values() if
                             player["id"] in best_alternatives_ids]

        self._sort_players_on_attribute(
            "PLAYER_VALUE", best_alternatives)

        if len(best_alternatives) > 5:
            return best_alternatives[::-1][:5]
        else:
            return best_alternatives[::-1]

    def get_optimal_team(self, position_dict, budget=100.0, gws_to_consider=10):
        """ An attempt to pick the optimal team for the upcomming gws with a
        linear programming approach. Inspired by this blogpost:
        https://medium.com/@joseph.m.oconnor.88/linearly-optimising-fantasy-premier-league-teams-3b76e9694877

        Args:
            position_dict (dict): The position_player_dict to consider.
            budget (float, optional): Transfer budget. Defaults to 100.0.
            gws_to_consider (int, optional): Gameweeks to consider (defaults to remaning but 1 and 5 is also viable alternatives).

        Returns:
            Tuple(list, String): Tuple containing a list of the best team and the best player to captain.
        """

        to_consider_dict = {
            1: "PLAYER_VALUE",
            5: "PLAYER_5_VALUE",
            10: "PLAYER_REMAINING_VALUE"
        }

        # Should not be necessary but preventing myself from errors for now
        if gws_to_consider not in to_consider_dict.keys():
            error("Choose a better value for gws_to_consider")

        attribute = to_consider_dict[gws_to_consider]

        # get all players in a list
        all_players = position_dict["Goalkeepers"] + position_dict["Defenders"] + \
            position_dict["Midfielders"] + position_dict["Forwards"]

        # filter out injured players
        all_players = list(filter(lambda x: x["status"] == "a", all_players))

        df = pd.DataFrame(all_players)

        player_values = df[attribute]
        prices = df["now_cost"]
        teams = df["team"]
        positions = df["element_type"]
        names = df["web_name"]

        best_players, best_captain, best_subs = self._get_optimal_team(
            player_values, prices, teams, positions, budget)

        starting_players = []
        captain_name = ""
        benchwarmers = []

        for i in range(df.shape[0]):
            if best_players[i].value() != 0:
                starting_players.append((names[i], teams[i], positions[i]))
            if best_captain[i].value() == 1:
                captain_name = names[i]
            if best_subs[i].value() != 0:
                benchwarmers.append((names[i], teams[i], positions[i]))

        return starting_players, captain_name, benchwarmers

    def _get_optimal_team(self, player_values, prices, teams, positions, budget):
        """_summary_

        Args:
            player_values (list): list of all players values
            prices (float): list of corresponding player costs
            teams (int): list of corresponding teams players belong to
            positions (int): list of corresponding player position
            budget (float): transfer budget

        Returns:
            Tuple(list, String): Tuple containing a list of the best team and the best player to captain.
        """

        num_players = len(player_values)
        model = pulp.LpProblem(
            "Constrained value maximisation", pulp.LpMaximize)
        decisions = [
            pulp.LpVariable("x{}".format(i), lowBound=0,
                            upBound=1, cat='Integer')
            for i in range(num_players)
        ]
        captain_decisions = [
            pulp.LpVariable("y{}".format(i), lowBound=0,
                            upBound=1, cat='Integer')
            for i in range(num_players)
        ]
        sub_decisions = [
            pulp.LpVariable("z{}".format(i), lowBound=0,
                            upBound=1, cat='Integer')
            for i in range(num_players)
        ]

        # objective function:
        model += sum((captain_decisions[i] + decisions[i] + sub_decisions[i]*0.2) * player_values[i]
                     for i in range(num_players)), "Objective"

        # cost constraint
        model += sum((decisions[i] + sub_decisions[i]) * prices[i]
                     for i in range(num_players)) <= budget

        # position constraints
        # 1 starting goalkeeper
        model += sum(decisions[i]
                     for i in range(num_players) if positions[i] == 1) == 1
        # 2 total goalkeepers
        model += sum(decisions[i] + sub_decisions[i]
                     for i in range(num_players) if positions[i] == 1) == 2

        # 3-5 starting defenders
        model += sum(decisions[i]
                     for i in range(num_players) if positions[i] == 2) >= 3
        model += sum(decisions[i]
                     for i in range(num_players) if positions[i] == 2) <= 5
        # 5 total defenders
        model += sum(decisions[i] + sub_decisions[i]
                     for i in range(num_players) if positions[i] == 2) == 5

        # 3-5 starting midfielders
        model += sum(decisions[i]
                     for i in range(num_players) if positions[i] == 3) >= 3
        model += sum(decisions[i]
                     for i in range(num_players) if positions[i] == 3) <= 5
        # 5 total midfielders
        model += sum(decisions[i] + sub_decisions[i]
                     for i in range(num_players) if positions[i] == 3) == 5

        # 1-3 starting attackers
        model += sum(decisions[i]
                     for i in range(num_players) if positions[i] == 4) >= 1
        model += sum(decisions[i]
                     for i in range(num_players) if positions[i] == 4) <= 3
        # 3 total attackers
        model += sum(decisions[i] + sub_decisions[i]
                     for i in range(num_players) if positions[i] == 4) == 3

        # club constraint
        for club_id in set(teams):
            model += sum(decisions[i] + sub_decisions[i] for i in range(
                num_players) if teams[i] == club_id) <= 3  # max 3 players

        model += sum(decisions) == 11  # total team size
        model += sum(captain_decisions) == 1  # 1 captain
        model += sum(sub_decisions) == 4  # 4 subs

        for i in range(num_players):
            # captain must also be on team
            model += (decisions[i] - captain_decisions[i]) >= 0
            # subs must not be on team
            model += (decisions[i] + sub_decisions[i]) <= 1

        model.solve()

        return decisions, captain_decisions, sub_decisions

    def user_friendly_result(self, starting_eleven, bench, id_team_dict, id_position_dict):
        """ Method for providing more information about the optimal eleven to the user

        Args:
            starting_eleven (list): the information about the players in the starting eleven
            bench (list): the information about the players on the bench
            id_team_dict (dict): dict containing the string value of the team
            id_position_dict (dict): dict containing the string value of the position

        Returns:
            (dict, list): the user friendlier result of the starting eleven and bench players
        """
        eleven_dict = {}
        bench_list = []

        for player_info in starting_eleven:
            name, team, pos = player_info
            pos = id_position_dict[pos]
            team = id_team_dict[team]
            if pos in eleven_dict:
                eleven_dict[pos].append((name, team))
            else:
                eleven_dict[pos] = [(name, team)]

        for player_info in bench:
            name, team, pos = player_info
            pos = id_position_dict[pos]
            team = id_team_dict[team]
            bench_list.append((name, pos, team))

        return eleven_dict, bench_list

    def readable_ranking_list(self, player_list, attribute, id_team_dict):
        """ Makes the ranking result more user friendly.

        Args:
            player_list (list): List of the best players
            attribute (String): The sorting attribute
            id_team_dict (dict): The dict containing team names as values

        Returns:
            list: list of tuples containing readable info
        """

        readable_list = []

        for rank, player in enumerate(player_list):
            readable_list.append(
                (rank+1, player["web_name"], player[attribute], id_team_dict[player["team"]]))

        return readable_list
