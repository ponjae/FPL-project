from flask import Flask, render_template, request
from fplData import playerData, playerEvaluation, playerRanking, gameData

app = Flask(__name__)
gd = gameData.gameData()
pd = playerData.playerData()
pe = playerEvaluation.playerEvaluation()
pe.add_player_values(pd.position_and_player_dict)
pe.add_player_values(pd.team_and_player_dict)
pr = playerRanking.playerRanking()
all_players = pd.position_and_player_dict["Goalkeepers"] + pd.position_and_player_dict["Defenders"] + \
    pd.position_and_player_dict["Midfielders"] + \
    pd.position_and_player_dict["Forwards"]
player_id_dict = pd.player_and_data_dict


@app.route("/")
def home():
    gameweek_data = gd.gw_data
    gw_games = gd.convert_fixtures(pd.id_team_dict)

    return render_template("index.html", gw_data=gameweek_data, id_player=player_id_dict, gw_games=gw_games)


@app.route("/your-team-config")
def your_team_config():
    goalkeepers = pd.position_and_player_dict["Goalkeepers"]
    defenders = pd.position_and_player_dict["Defenders"]
    midfielders = pd.position_and_player_dict["Midfielders"]
    forwards = pd.position_and_player_dict["Forwards"]
    id_team_dict = pd.id_team_dict

    return render_template("your-config.html", goalkeepers=goalkeepers, defenders=defenders, midfielders=midfielders, forwards=forwards, id_team_dict=id_team_dict)


@app.route("/your-team", methods=["POST", "GET"])
def your_team():
    if request.method == "POST":
        g1 = player_id_dict[int(request.form["goalkeeper1"])]
        g2 = player_id_dict[int(request.form["goalkeeper2"])]

        d1 = player_id_dict[int(request.form["defender1"])]
        d2 = player_id_dict[int(request.form["defender2"])]
        d3 = player_id_dict[int(request.form["defender3"])]
        d4 = player_id_dict[int(request.form["defender4"])]
        d5 = player_id_dict[int(request.form["defender5"])]

        m1 = player_id_dict[int(request.form["midfielder1"])]
        m2 = player_id_dict[int(request.form["midfielder2"])]
        m3 = player_id_dict[int(request.form["midfielder3"])]
        m4 = player_id_dict[int(request.form["midfielder4"])]
        m5 = player_id_dict[int(request.form["midfielder5"])]

        f1 = player_id_dict[int(request.form["forward1"])]
        f2 = player_id_dict[int(request.form["forward2"])]
        f3 = player_id_dict[int(request.form["forward3"])]

        itb = float(request.form["ITB"])

        team = [g1, g2, d1, d2, d3, d4, d5, m1, m2, m3, m4, m5, f1, f2, f3]
        curr_team = [player["web_name"] for player in team]

        gw1_team = pr.under_performers(team, 1)
        # Three transfer suggestions
        transfer_sug1 = pr.transfer_suggestion(
            gw1_team[0]["id"], player_id_dict, itb)
        transfer_sug1 = [player["web_name"] for player in transfer_sug1]

        transfer_sug2 = pr.transfer_suggestion(
            gw1_team[1]["id"], player_id_dict, itb)
        transfer_sug2 = [player["web_name"] for player in transfer_sug2]

        transfer_sug3 = pr.transfer_suggestion(
            gw1_team[2]["id"], player_id_dict, itb)
        transfer_sug3 = [player["web_name"] for player in transfer_sug3]

        gw1_team = [player["web_name"] for player in gw1_team]
        transfer1gw = {
            "player1": gw1_team[0],
            "suggestions1": transfer_sug1,
            "player2": gw1_team[1],
            "suggestions2": transfer_sug2,
            "player3": gw1_team[2],
            "suggestions3": transfer_sug3,
        }

        gw5_team = pr.under_performers(team, 5)
        # Three transfer suggestions
        transfer_sug1 = pr.transfer_suggestion(
            gw5_team[0]["id"], player_id_dict, itb)
        transfer_sug1 = [player["web_name"] for player in transfer_sug1]

        transfer_sug2 = pr.transfer_suggestion(
            gw5_team[1]["id"], player_id_dict, itb)
        transfer_sug2 = [player["web_name"] for player in transfer_sug2]

        transfer_sug3 = pr.transfer_suggestion(
            gw5_team[2]["id"], player_id_dict, itb)
        transfer_sug3 = [player["web_name"] for player in transfer_sug3]

        gw5_team = [player["web_name"] for player in gw5_team]
        transfer5gw = {
            "player1": gw5_team[0],
            "suggestions1": transfer_sug1,
            "player2": gw5_team[1],
            "suggestions2": transfer_sug2,
            "player3": gw5_team[2],
            "suggestions3": transfer_sug3,
        }

        gw_rem_team = pr.under_performers(team, 10)
        gw_rem_team = [player["web_name"] for player in gw_rem_team]

        points_team = pr.under_performers(team, 2)
        points_team = [player["web_name"] for player in points_team]

        return render_template("your-team.html", current_team=curr_team, gw1_team=gw1_team, gw5_team=gw5_team, gw_rem_team=gw_rem_team, points_team=points_team, gw1_transfer=transfer1gw, gw5_transfer=transfer5gw, len=len)
    else:
        return render_template('404.html'), 404


@app.route("/player-ranking")
def player_ranking():
    ranking_dict = get_ranking_lists(all_players, pd.id_team_dict)

    return render_template("ranking.html", round=round, form=ranking_dict["form"], now_cost=ranking_dict["now_cost"],
                           points_per_game=ranking_dict["points_per_game"], selected_by_percent=ranking_dict["selected_by_percent"],
                           total_points=ranking_dict["total_points"], transfers_in=ranking_dict["transfers_in"],
                           transfers_out=ranking_dict["transfers_out"], minutes=ranking_dict[
                               "minutes"], goals_scored=ranking_dict["goals_scored"],
                           cheapest=ranking_dict["cheapest"], assists=ranking_dict["assists"], penalties_saved=ranking_dict[
                               "penalties_saved"], saves=ranking_dict["saves"],
                           points_per_million=ranking_dict["points_per_million"], PLAYER_VALUE=ranking_dict["PLAYER_VALUE"],
                           PLAYER_5_VALUE=ranking_dict["PLAYER_5_VALUE"], PLAYER_REMAINING_VALUE=ranking_dict["PLAYER_REMAINING_VALUE"])


@app.route("/best-team-configurations")
def best_team_config():
    return render_template("config.html")


@app.route("/best-team", methods=["POST", "GET"])
def best_team():
    if request.method == "POST":
        budget = float(request.form["budget"])
        to_consider = int(request.form["to_consider"])
        heading_text_dict = {
            1: "next Gw",
            5: "next 5 Gw:s",
            10: "remaining Gw:s"
        }
        eleven, captain, bench = pr.get_optimal_team(
            pd.position_and_player_dict, budget, to_consider)
        starting_eleven, bench_info = pr.user_friendly_result(
            eleven, bench, pd.id_team_dict, pd.id_position_dict)
        return render_template("optimal.html", starting_eleven=starting_eleven, bench=bench_info, captain=captain, heading_text=heading_text_dict[to_consider], budget=budget)
    else:
        return render_template("config.html")


@app.route("/teams/<team>")
def team_page(team):
    team_data = pd.team_and_player_dict[team]
    color_scheme = ''.join(team.split(" "))
    if color_scheme == "Nott'mForest":
        color_scheme = "Nott'm Forest"
    elif color_scheme == 'SheffieldUtd':
        color_scheme = 'Sheffield'
    position_dict = pd.id_position_dict
    team_data_dict = gd.team_data_dict


    return render_template("team.html", scheme=color_scheme, team_data=team_data, position_dict=position_dict, round=round, team_data_dict=team_data_dict[color_scheme])


@app.route("/about")
def about():
    return render_template("about.html")


@app.errorhandler(404)
def page_not_found(e):
    # note that we set the 404 status explicitly
    return render_template('404.html'), 404


if __name__ == '__main__':
    app.run()


def get_ranking_lists(players, id_team_dict):
    """ Method for generating the rankinglists to be displayed at ranking.html

    Args:
        players (list): all players available
        id_team_dict (dict): dict of teams

    Returns:
        dict: dict of ranking lists
    """
    attributes = ["form", "now_cost", "points_per_game", "selected_by_percent", "total_points", "transfers_in", "transfers_out", "minutes",
                  "goals_scored", "assists", "penalties_saved", "saves", "points_per_million", "PLAYER_VALUE", "PLAYER_5_VALUE", "PLAYER_REMAINING_VALUE"]

    ranking_dict = {}

    for attribute in attributes:
        temp = pr.get_most_valuable_list(attribute, players, 10)
        ranking_dict[attribute] = pr.readable_ranking_list(
            temp, attribute, id_team_dict)

    ranking_dict["cheapest"] = pr.readable_ranking_list(
        pr.get_most_valuable_list("now_cost", players, 10, False), "now_cost", id_team_dict)

    return ranking_dict
