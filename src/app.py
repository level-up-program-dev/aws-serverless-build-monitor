from functools import cache
from typing import Dict, List

from dateutil import parser
from flask import Flask, render_template, request
from munch import Munch

from aws import get_json_object, repo_cache_list
from constants import S3_CACHE_BUCKET
from models.team import TeamModel

app = Flask(__name__)
app.url_map.strict_slashes = False
app.jinja_options["extensions"] = ["jinja2_humanize_extension.HumanizeExtension"]


@cache
def get_repo_name_for_team(team_number: str, event_id: str) -> str:
    try:
        team_number = int(team_number)
        team = TeamModel.get(team_number, event_id)
    except TeamModel.DoesNotExist:
        pass
    except ValueError:
        pass  # if the team_number cannot be convert to an integer
    else:
        return team.repo_name


def get_data_from_s3(repo_names: List) -> Dict:
    data = []
    all_objects = repo_cache_list()
    for repo_name in repo_names:
        json_object_key = f"{repo_name}.json"
        if json_object_key in all_objects:
            json_obj = get_json_object(S3_CACHE_BUCKET, json_object_key)
            obj = Munch.fromDict(json_obj)  # Convert dict to object
            obj.head_commit.timestamp = parser.parse(obj.head_commit.timestamp[:-1])
            data.append(obj)
    return data


@app.route("/")
def home():
    event_id = request.args.get("event_id")
    team_numbers = [x for x in request.args.get("team_numbers", "").strip(",").split(",") if x]
    team_repo_names = [x for x in [get_repo_name_for_team(t, event_id) for t in team_numbers] if x]

    if "repo_name" in request.args:
        team_repo_names = [request.args.get("repo_name")]

    data = get_data_from_s3(team_repo_names)
    return render_template(
        "index.html",
        data=data,
    )
