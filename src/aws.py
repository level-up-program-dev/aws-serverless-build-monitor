import json
import logging
from functools import cache
from typing import Dict

import boto3
from botocore.errorfactory import ClientError

from constants import S3_CACHE_BUCKET

logger = logging.getLogger()


def write_dict_to_json_s3(dict_object: Dict, keypath: str) -> None:
    logger.info(f"Writing {keypath} to S3")
    json_string = json.dumps(dict_object, indent=4, default=str)
    s3 = boto3.resource("s3")
    s3.Bucket(S3_CACHE_BUCKET).put_object(
        Body=json_string.encode("utf-8"), ContentType="application/json", Key=keypath
    )


def s3_key_exists(bucket, key):
    s3 = boto3.client("s3")
    try:
        s3.head_object(Bucket=bucket, Key=key)
        return True
    except ClientError as err:
        if "404" in str(err):
            return False
        raise


def list_objects_generator(bucket, prefix=None, paginator="list_objects_v2"):
    s3 = boto3.client("s3")
    param_dict = {"Bucket": bucket}
    if prefix:
        param_dict["Prefix"] = prefix
    response_iterator = s3.get_paginator(paginator).paginate(**param_dict)
    for response in response_iterator:
        yield response


@cache
def repo_cache_list():
    keys = []
    for x in list_objects_generator(S3_CACHE_BUCKET):
        for obj in x["Contents"]:
            keys.append(obj["Key"])
    return keys


@cache
def get_json_object(bucket: str, key: str):
    s3 = boto3.client("s3")
    obj = s3.get_object(Bucket=bucket, Key=key)
    return json.loads(obj["Body"].read().decode("utf-8"))
