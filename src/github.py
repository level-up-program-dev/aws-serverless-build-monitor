import asyncio
import json
import logging
from pathlib import Path
from typing import Dict, List

import boto3
from fastcore.xtras import obj2dict
from ghapi.all import GhApi

from aws import write_dict_to_json_s3
from constants import GH_ORG

api = GhApi()
logger = logging.getLogger()
logger.setLevel(logging.INFO)


def get_repo_list():
    # https://docs.github.com/en/rest/repos/repos?apiVersion=2022-11-28#list-organization-repositories
    return [
        r["name"]
        for r in api.repos.list_for_org(
            GH_ORG, type="Public", sort="full_name", per_page=100
        )
    ]


def get_latest_workflow_run(repo_name: str) -> List:
    # https://docs.github.com/en/rest/actions/workflow-runs?apiVersion=2022-11-28#list-workflow-runs-for-a-repository
    return api.actions.list_workflow_runs_for_repo(
        GH_ORG, repo_name, branch="main", per_page=1
    )["workflow_runs"]


def get_workflow_jobs(repo_name: str, workflow_run_id: str) -> Dict:
    # https://docs.github.com/en/rest/actions/workflow-jobs?apiVersion=2022-11-28#list-jobs-for-a-workflow-run
    return api.actions.list_jobs_for_workflow_run(
        GH_ORG, repo_name, workflow_run_id, per_page=100
    )["jobs"]


def write_dict_to_json_file(dict_object: Dict, filepath: str) -> None:
    json_string = json.dumps(dict_object, indent=4, default=str)
    with open(filepath, "w") as outfile:
        outfile.write(json_string)


async def get_repo_data(repo_name: str, cache: bool=False) -> None:
    logger.info(f"Retrieving workflow runs for repo: {repo_name}")

    # There should only ever be 1 thing in this list, but it will be a list
    for workflow_run in get_latest_workflow_run(repo_name):
        logger.info(f"Found workflow run for repo: {repo_name}")
        required_keys = [
            "id",
            "name",
            "workflow_id",
            "display_title",
            "run_started_at",
            "status",
            "conclusion",
            "html_url",
            "repository",
            "head_branch",
            "head_commit",
            "triggering_actor",
        ]
        wf_data = {k: workflow_run[k] for k in required_keys}
        wf_data["jobs"] = []
        run_id = wf_data["id"]
        logger.info(f"Retrieving workflow jobs for {repo_name}:{run_id}")
        for job in get_workflow_jobs(repo_name, run_id):
            logger.info(f"Found workflow jobs for {repo_name}:{run_id}")
            wf_data["jobs"].append(job)
            if job["name"].lower() == "build-and-test":
                # Overwrite workflow status with build-and-test status
                wf_data["conclusion"] = job["conclusion"]
        repo_data = obj2dict(wf_data)
        if cache:
            write_dict_to_json_s3(repo_data, f"{repo_name}.json")

        return repo_data
    
    return None


async def get_all_repo_data(cache: bool=True):
    coro_objs = []
    for repo_name in get_repo_list():
        coro_objs.append(get_repo_data(repo_name, cache=cache))
    results = await asyncio.gather(*coro_objs)
    return results


def handler(*args):
    asyncio.run(get_all_repo_data())
