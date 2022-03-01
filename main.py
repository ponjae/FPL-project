import imp
from flask import Flask, render_template
# from fplData import playerData, playerEvaluation, playerRanking
from secrets import secret

app = Flask(__name__)


@app.route("/")
def home():
    return render_template("index.html", secret=secret["font_awesome"])


@app.errorhandler(404)
def page_not_found(e):
    # note that we set the 404 status explicitly
    return render_template('404.html'), 404


if __name__ == '__main__':
    app.run()
