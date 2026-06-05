from flask import Flask, jsonify, request
from scripts.helpers import (
    get_message_text,
    get_thread_permalink,
    has_recent_channel_post,
    is_url_verification_challenge,
    parse_event_data,
    post_to_slack,
    is_request_valid
)
from scripts.database import (
    DatabaseError,
    insert_new_event,
    update_event
)

app = Flask(__name__)

@app.route("/slack/events", methods=['POST'])
def accept_events():
    """Route handler for all requests that come through"""
    data = request.get_json()

    # If the request is for URL verification, handle that and return
    if is_url_verification_challenge(data):
        return jsonify({"challenge": data['challenge']}), 200

    # Validate request
    if not is_request_valid(
        request_body=request.get_data(),
        timestamp=request.headers['X-Slack-Request-Timestamp'],
        slack_signature=request.headers['x-slack-signature']
    ):
        return "Request not verified", 400

    # Otherwise, we're getting a request from an event in our workspace

    # First, add all incoming events to database
    try:
        event_id = insert_new_event(data)
    except DatabaseError as e:
        return str(e), 500

    # Parse event data
    info = parse_event_data(data)
    if info is None:
        try:
            update_event(event_id, {'status': 'rejected'})
        except DatabaseError as e:
            return str(e), 500
        return "", 204

    # Update database to mark as 'processed'
    try:
        update_event(event_id, {'status': 'accepted'})
    except DatabaseError as e:
        return str(e), 500

    channel = info['channel']
    parent_post_ts = info['parent_post_ts']
    course_name = info['course_name']
    course_channel_id = info['slack_channel_id']

    # If there hasn't been a recent post made, post in the course channel
    if not has_recent_channel_post(course_channel_id, parent_post_ts):
        # Post to the channel
        permalink = get_thread_permalink(channel, parent_post_ts)
        post_to_slack(
            course_channel_id,
            {"blocks": get_message_text(course_name, permalink)}
        )
        try:
            update_event(event_id, {'channel_post_sent': True})
        except DatabaseError as e:
            return str(e), 500

    return "OK", 200

if __name__ == "__main__":
    app.run(debug=True, port=5003)
