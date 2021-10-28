import os
import urllib

import requests
import requests.auth
from flask import abort, request, Flask

app = Flask(__name__)

CLIENT_ID = os.environ['REDDIT_CLIENT_ID']
CLIENT_SECRET = os.environ['REDDIT_CLIENT_SECRET']
REDIRECT_URI = "http://localhost:65010/reddit_callback"

# Global variables
access_token = None
global_state = None


@app.route('/')
def homepage():
    text = '<a href="%s">Authenticate with reddit</a>'
    return text % make_authorization_url()


def make_authorization_url():
    # Generate a random string for the state parameter
    # Save it for use later to prevent xsrf attacks
    from uuid import uuid4
    state = str(uuid4())
    save_created_state(state)
    params = {"client_id": CLIENT_ID,
              "response_type": "code",
              "state": state,
              "redirect_uri": REDIRECT_URI,
              "duration": "temporary",
              "scope": "identity, read"}
    url = "https://ssl.reddit.com/api/v1/authorize?" + \
          urllib.parse.urlencode(params)
    return url


@app.route('/reddit_callback')
def reddit_callback():
    error = request.args.get('error', '')
    if error:
        return "Error: " + error
    state = request.args.get('state', '')
    if not is_valid_state(state):
        # Uh-oh, this request wasn't started by us!
        abort(403)
    code = request.args.get('code')
    # We'll change this next line in just a moment

    try:
        global access_token
        access_token = get_token(code)
        return access_token
    except Exception:
        return "ERROR"


def get_token(code):
    client_auth = requests.auth.HTTPBasicAuth(CLIENT_ID, CLIENT_SECRET)
    post_data = {"grant_type": "authorization_code",
                 "code": code,
                 "redirect_uri": REDIRECT_URI}
    response = requests.post("https://ssl.reddit.com/api/v1/access_token",
                             headers={'User-agent': 'your bot 0.1'},
                             auth=client_auth,
                             data=post_data)

    token_json = response.json()
    return token_json["access_token"]


@app.route('/userdata')
def get_username():
    global access_token
    headers = {"Authorization": "bearer " + access_token, 'User-agent': 'your bot 0.1'}
    response = requests.get(
        "https://oauth.reddit.com/api/v1/me", headers=headers)
    return response.json()


@app.route('/friends')
def get_friends():
    global access_token
    headers = {"Authorization": "bearer " + access_token, 'User-agent': 'your bot 0.1'}
    response = requests.get(
        "https://oauth.reddit.com/api/v1/me/friends", headers=headers)

    return response.json()


def save_created_state(state):
    global global_state
    global_state = state


def is_valid_state(state):
    global global_state
    return global_state == state


if __name__ == '__main__':
    app.run(debug=True, port=65010)
