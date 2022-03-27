import re
from flask import Flask, render_template, request
from fplData import playerData, playerEvaluation, playerRanking, gameData
from secrets import secret

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


@app.route("/")
def home():
    id_player_dict = pd.player_and_data_dict
    gameweek_data = gd.gw_data
    gw_games = gd.convert_fixtures(pd.id_team_dict)

    return render_template("index.html", secret=secret["font_awesome"], gw_data=gameweek_data, id_player=id_player_dict, gw_games=gw_games)


@app.route("/your-team-config")
def your_team_config():
    goalkeepers = pd.position_and_player_dict["Goalkeepers"]
    defenders = pd.position_and_player_dict["Defenders"]
    midfielders = pd.position_and_player_dict["Midfielders"]
    forwards = pd.position_and_player_dict["Forwards"]

    return render_template("your-config.html", secret=secret["font_awesome"], goalkeepers=goalkeepers, defenders=defenders, midfielders=midfielders, forwards=forwards)


@app.route("/player-ranking")
def player_ranking():
    ranking_dict = get_ranking_lists(all_players, pd.id_team_dict)

    return render_template("ranking.html", secret=secret["font_awesome"], round=round, form=ranking_dict["form"], now_cost=ranking_dict["now_cost"],
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
    return render_template("config.html", secret=secret["font_awesome"])


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
        return render_template("optimal.html", secret=secret["font_awesome"],  starting_eleven=starting_eleven, bench=bench_info, captain=captain, heading_text=heading_text_dict[to_consider], budget=budget)
    else:
        return render_template("config.html", secret=secret["font_awesome"])


@app.route("/teams/<team>")
def team_page(team):
    team_data = pd.team_and_player_dict[team]
    color_scheme = ''.join(team.split(" "))
    position_dict = pd.id_position_dict
    team_data_dict = gd.team_data_dict
    return render_template("team.html",  secret=secret["font_awesome"], scheme=color_scheme, team_data=team_data, position_dict=position_dict, round=round, team_data_dict=team_data_dict[color_scheme])


@app.route("/about")
def about():
    return render_template("about.html", secret=secret["font_awesome"])


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
