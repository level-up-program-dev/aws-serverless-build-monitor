from botocore.exceptions import ClientError
from .team import TeamModel

def is_conditional_error(e):
    if isinstance(e.cause, ClientError):
        code = e.cause.response["Error"].get("Code")
        if code == "ConditionalCheckFailedException":
            return True
