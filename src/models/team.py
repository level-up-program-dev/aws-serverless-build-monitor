from pynamodb.attributes import ListAttribute, NumberAttribute, UnicodeAttribute
from pynamodb.constants import PAY_PER_REQUEST_BILLING_MODE, STREAM_NEW_AND_OLD_IMAGE
from pynamodb.models import Model

from constants import AWS_DEFAULT_REGION, DYNAMODB_ENDPOINT, GH_ORG_URL

from .attributes import UUIDAttribute


class TeamModel(Model):
    class Meta:
        table_name = "levelup-teams"
        region = AWS_DEFAULT_REGION
        stream_view_type = STREAM_NEW_AND_OLD_IMAGE
        billing_mode = PAY_PER_REQUEST_BILLING_MODE
        if DYNAMODB_ENDPOINT:
            host = DYNAMODB_ENDPOINT

    team_number = NumberAttribute(hash_key=True)
    event_uid = UUIDAttribute(range_key=True)
    classroom_number = NumberAttribute()
    name = UnicodeAttribute()
    num_members = NumberAttribute()
    tech_stack = UnicodeAttribute()
    repo_url = UnicodeAttribute(null=True)
    env_urls = ListAttribute(null=True)

    @property
    def repo_name(self):
        return self.repo_url.replace(GH_ORG_URL, "").strip("/")
