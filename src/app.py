from flask import Flask, redirect, render_template, request, jsonify
from github import get_all_repo_data

app = Flask(__name__)
app.url_map.strict_slashes = False
app.jinja_options["extensions"] = ["jinja2_humanize_extension.HumanizeExtension"]


@app.route("/")
def home():
    event_id = request.args.get("event_id")
    team_number_list = request.args.get("team_number_list", "").split(",")
    data = []  # get_all_repo_data(event_id, team_number_list)
    return render_template(
        "index.html",
        event_id=event_id,
        team_number_list=team_number_list,
        data=data,
    )
