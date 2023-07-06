import logging
import os
from pathlib import Path

from jinja2 import Environment, FileSystemLoader

from utils import makeQR

#########################
# Logging Setup
#########################

LOGGER = logging.getLogger()
LOGGER.setLevel(logging.INFO)

#########################
# Flask Specific
#########################

ROOT_DIR = Path(__file__).parent
TEMPLATE_ROOT_DIR = ROOT_DIR.joinpath("templates")
ENV = Environment(
    loader=FileSystemLoader(TEMPLATE_ROOT_DIR),
    autoescape=True,
    extensions=["jinja2_humanize_extension.HumanizeExtension"],
)
ENV.filters["makeQR"] = makeQR

#########################
# Application Specific
#########################

SITE_URL = os.environ.get("SITE_URL", "http://localhost:8000")
GH_ORG = "level-up-program"
GH_ORG_URL = f"https://github.com/{GH_ORG}/"

#########################
# AWS
#########################

AWS_DEFAULT_REGION = os.environ.get("AWS_DEFAULT_REGION", "us-east-2")
DYNAMODB_ENDPOINT = os.environ.get("DYNAMODB_ENDPOINT")
