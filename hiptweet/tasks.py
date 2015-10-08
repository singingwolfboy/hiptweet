import logging
import requests
from flask import Blueprint, jsonify
from requests_oauthlib import OAuth2Session
from hiptweet import celery
from hiptweet.models import HipChatGroup, HipChatRoom
from celery.utils.log import get_task_logger

# set up logging
logger = get_task_logger(__name__)
logger.setLevel(logging.INFO)

# create a Flask blueprint for getting task status info
tasks = Blueprint('tasks', __name__)

@tasks.route('/status/<task_id>')
def status(task_id):
    result = celery.AsyncResult(task_id)
    return jsonify({"status": result.state})


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
    session = OAuth2Session(token=group.twitter_oauth.token)
    rooms_info = paginated_get("/v2/rooms", session=session)
    for room_info in rooms_info:
        room_id = room_info['id']
        room = HipChatRoom.query.get(room_id)
        if not room:
            room = HipChatRoom(id=room_id, group=group)
        room.name = room_info["name"]
        db.session.add(room)
    db.session.commit()
