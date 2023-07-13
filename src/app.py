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


def get_team_repos_for_classroom(event_id: str, classroom_number: str) -> list:
    try:
        classroom_number = int(classroom_number)
        team_repos = sorted(
            [
                t.repo_name
                for t in TeamModel.scan()
                if str(t.event_uid) == event_id and t.classroom_number == classroom_number
            ]
        )
    except (ValueError, TypeError):
        team_repos = []  # if the classroom_number cannot be convert to an integer

    return team_repos


def get_data_from_s3(repo_names: List) -> List:
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
    if "repo_name" in request.args:
        team_repo_names = [request.args.get("repo_name")]
    else:
        event_id = request.args.get("event_id")
        classroom_number = request.args.get("classroom_number")
        team_repo_names = get_team_repos_for_classroom(event_id=event_id, classroom_number=classroom_number)

    data = get_data_from_s3(team_repo_names)
    return render_template(
        "index.html",
        data=data,
    )
