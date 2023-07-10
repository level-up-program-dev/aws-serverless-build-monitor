import asyncio
from functools import cache
from typing import Dict, List

from dateutil import parser
from flask import Flask, jsonify, redirect, render_template, request
from munch import Munch

from aws import get_json_object, list_objects_generator, repo_cache_list
from constants import S3_CACHE_BUCKET
from github import get_all_repo_data
from models.team import TeamModel

app = Flask(__name__)
app.url_map.strict_slashes = False
app.jinja_options["extensions"] = ["jinja2_humanize_extension.HumanizeExtension"]


@cache
def get_repo_name_for_team(team_number: int, event_id: str) -> str:
    try:
        team = TeamModel.get(team_number, event_id)
    except TeamModel.DoesNotExist:
        pass
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
    team_number_list = [x for x in request.args.get("team_number_list", "").strip(",").split(",") if x]
    team_repo_names = [x for x in [get_repo_name_for_team(int(t), event_id) for t in team_number_list] if x]
    data = get_data_from_s3(team_repo_names)
    return render_template(
        "index.html",
        event_id=event_id,
        team_number_list=team_number_list,
        team_repo_names=team_repo_names,
        data=data,
    )
