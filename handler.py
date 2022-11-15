import logging
from pathlib import Path
from dateutil import parser
from typing import Dict, List
from ghapi.all import GhApi
from fastcore.net import HTTP404NotFoundError
from jinja2 import Environment, FileSystemLoader
import boto3


GH_ORG = "level-up-program"
TEMPLATE_ROOT_DIR = Path("./templates")
environment = Environment(
    loader=FileSystemLoader(TEMPLATE_ROOT_DIR),
    extensions=["jinja2_humanize_extension.HumanizeExtension"],
    autoescape=True,
)
template = environment.get_template("index.html")

api = GhApi()
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def get_branch(repo: str, branch_name: str) -> Dict:
    refname = f"heads/{branch_name}"
    return api.git.get_ref(GH_ORG, repo, refname)


def get_repo_list():
    return api.repos.list_for_org(GH_ORG, type="Public", sort="full_name", per_page=100)


def get_workflow_runs(repo: str, sha: str) -> List:
    return api.actions.list_workflow_runs_for_repo(
        GH_ORG, repo, branch="main", head_sha=sha, per_page=100
    )["workflow_runs"]


def get_workflow_jobs(repo: str, workflow_run_id: str) -> Dict:
    return api.actions.list_jobs_for_workflow_run(
        GH_ORG, repo, workflow_run_id, per_page=100
    )["jobs"]


def get_all_repo_data() -> List:
    repo_data = []
    for repo in get_repo_list():
        repo_name = repo["name"]
        logger.info(f"Found repo {repo_name}")
        if not repo_name.startswith("team-"):
            continue
        try:
            headref = get_branch(repo_name, repo["default_branch"])
        except HTTP404NotFoundError:
            continue
        else:
            commit_sha = headref["object"]["sha"]
            repo["workflows"] = []
            repo["head_ref"] = {}
            for workflow_run in get_workflow_runs(repo_name, commit_sha):
                repo["head_ref"]["actor"] = workflow_run["triggering_actor"]
                repo["head_ref"]["commit"] = workflow_run["head_commit"]
                repo["head_ref"]["commit"]["timestamp"] = parser.parse(
                    workflow_run["head_commit"]["timestamp"][:-1]
                )
                workflow_run_id = workflow_run["id"]
                workflow_run["jobs"] = []
                for job in get_workflow_jobs(repo_name, workflow_run_id):
                    workflow_run["jobs"].append(job)
                repo["workflows"].append(workflow_run)
            repo_data.append(repo)
    return repo_data


def main():
    data = get_all_repo_data()
    content = template.render(data=data)
    output_file_path = "index.html"
    s3 = boto3.resource("s3")
    s3.Bucket("monitor.levelup-program.com").put_object(
        Body=content.encode("utf-8"), ContentType="text/html", Key=output_file_path
    )


def run(event, context):
    main()


if __name__ == "__main__":
    main()
