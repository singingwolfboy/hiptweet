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
    return jsonify({
        "state": result.state,
        "info": result.info,
    })


def paginated_get(url, session=None, callback=None, **kwargs):
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
        if callable(callback):
            callback(resp)
        resp.raise_for_status()
        result = resp.json()
        for item in result["items"]:
            yield item
        url = result.get("links", {}).get("next", "")


@celery.task(bind=True)
def fetch_room_names(self, group_id):
    group = HipChatGroup.query.get(group_id)
    capabilities_url = group.install_info[0].capabilities_url
    capabilities_resp = requests.get(capabilities_url)
    capabilities_resp.raise_for_status()
    base_api_url = (
        capabilities_resp.json()["capabilities"]["hipchatApiProvider"]["url"]
    )
    rooms_info_url = base_api_url + "room"
    session = OAuth2Session(token=group.twitter_oauth.token)

    def update_state(resp):
        if not resp.ok:
            return
        start_index = resp.json()["startIndex"]
        self.update_state(state="STARTED", meta={"startIndex": start_index})

    rooms_info = paginated_get(rooms_info_url, session=session, callback=update_state)
    for room_info in rooms_info:
        room_id = room_info['id']
        room = HipChatRoom.query.get(room_id)
        if not room:
            room = HipChatRoom(id=room_id, group=group)
        room.name = room_info["name"]
        db.session.add(room)
    db.session.commit()
