import urllib
import os
from flask import abort, request, Flask
from dotenv import load_dotenv

app = Flask(__name__)


load_dotenv()

CLIENT_ID = os.getenv('REDDIT_CLIENT_ID')
CLIENT_SECRET = os.getenv('REDDIT_CLIENT_SECRET')
REDIRECT_URI = "http://localhost:65010/reddit_callback"



@app.route('/')
def homepage():
	text = '<a href="%s">Authenticate with reddit</a>'
	return text % make_authorization_url()

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
	return "got a code! %s" % code


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
			  "scope": "identity"}
	url = "https://ssl.reddit.com/api/v1/authorize?" + urllib.parse.urlencode(params)
	return url

# Left as an exercise to the reader.
# You may want to store valid states in a database or memcache,
# or perhaps cryptographically sign them and verify upon retrieval.
def save_created_state(state):
	pass
def is_valid_state(state):
	return True


if __name__ == '__main__':
	app.run(debug=True, port=65010)
