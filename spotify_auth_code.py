from flask import Flask, request, redirect
import webbrowser
import os
from urllib.parse import urlencode
from dotenv import load_dotenv

load_dotenv()

client_id = os.getenv("client_id")
redirect_uri = "http://localhost:5000/callback"

app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'Hello, visit /login to authorize.'

@app.route('/login')
def login():
    params = {
        "client_id": client_id,
        "response_type": "code",
        "redirect_uri": redirect_uri,
        "scope": "playlist-modify-public playlist-modify-private",
        # Add any other parameters you might need, like 'state' for CSRF protection
    }
    url = f"https://accounts.spotify.com/authorize?{urlencode(params)}"
    return redirect(url)

@app.route('/callback')
def callback():
    global auth_code
    auth_code = request.args.get('code')
    if auth_code:
        print("Authorization code:", auth_code)
        # Here you can add the code to exchange the authorization code for an access token
        return "Authorization successful! Check the console for the authorization code."
    else:
        return "Authorization failed."

if __name__ == '__main__':
    webbrowser.open_new("http://localhost:5000/login")
    app.run(debug=False)
