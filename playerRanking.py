from distutils.log import error
from playerData import playerData
from playerEvaluation import playerEvaluation

import pulp
import numpy as np
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

    def get_most_valuable_list(self, attribute, players, nbr):
        """ Returns the most valueable players depending on attribute.

        Args:
            attribute (string): the attribute in which to rank the players
            players (dict): the players from which the most valueable should be found
            nbr (int): how many players to return
        Returns:
            list: A list of with the most valueable players
        """

        self._sort_players_on_attribute(attribute, players)
        # Desc ordering
        players = players[::-1]
        assert nbr <= len(players)

        return players[:nbr]

    def get_optimal_team(self, position_dict, budget=100.0, gws_to_consider=5):
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
                starting_players.append(names[i])
            if best_captain[i].value() == 1:
                captain_name = names[i]
            if best_subs[i].value() != 0:
                benchwarmers.append(names[i])

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
        for club_id in np.unique(teams):
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
        print("Total expected score = {}".format(model.objective.value()))

        return decisions, captain_decisions, sub_decisions


player_data = playerData()
team_dict = player_data.team_and_player_dict
position_dict = player_data.position_and_player_dict
pe = playerEvaluation()
pe.add_player_values(position_dict)
pe.add_player_values(team_dict)
pr = playerRanking()

players, best_captain, subs = pr.get_optimal_team(
    position_dict, budget=103.0, gws_to_consider=10)
