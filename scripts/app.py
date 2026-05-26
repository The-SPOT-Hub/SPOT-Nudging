from flask import Flask, jsonify, request
from scripts.helpers import (
    EventRejectedError,
    get_message_text,
    get_thread_permalink,
    has_recent_channel_post,
    is_url_verification_challenge,
    parse_event_data,
    post_to_slack,
    is_request_valid
)

app = Flask(__name__)

@app.route("/slack/events", methods=['POST'])
def accept_events():
    """Route handler for all requests that come through"""
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

    data = request.get_json()

    # Otherwise, we're getting a request from an event in our workspace
    try:
        info = parse_event_data(data)
    except EventRejectedError as e:
        return str(e), 204

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

    return "OK", 200

if __name__ == "__main__":
    app.run(debug=True, port=5003)
