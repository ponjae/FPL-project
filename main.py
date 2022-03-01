import imp
from flask import Flask, render_template
# from fplData import playerData, playerEvaluation, playerRanking
from secrets import secret

app = Flask(__name__)


@app.route("/")
def home():
    return render_template("index.html", secret=secret["font_awesome"])


if __name__ == '__main__':
    app.run()
