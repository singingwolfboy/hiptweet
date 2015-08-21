import logging
import requests
from requests_oauthlib import OAuth2Session
from hiptweet import celery
from hiptweet.models import HipChatGroup
from celery.utils.log import get_task_logger

# set up logging
logger = get_task_logger(__name__)
logger.setLevel(logging.INFO)


def paginated_get(url, session=None, **kwargs):
    """
    Return a generator of results for this API call, based on the structure
    of HipChat's API return values.
    """
    session = session or requests.Session()
    payload = {
        "start-index": 0,
        "max-results": 1000,
    }
    payload.update(kwargs)
    while url:
        resp = session.get(url, params=payload)
        resp.raise_for_status()
        result = resp.json()
        for item in result["items"]:
            yield item
        url = result.get("links", {}).get("next", "")


@celery.task
def fetch_room_names(group_id):
    group = HipChatGroup.query.get(group_id)
    session = OAuth2Session(token=group.)
