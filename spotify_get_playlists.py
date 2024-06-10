import requests
import pandas as pd
from flask import Flask, request, redirect
import webbrowser
import os
from urllib.parse import urlencode
from dotenv import load_dotenv

load_dotenv()

client_id = os.getenv("client_id")
client_secret = os.getenv("client_secret")
redirect_uri = "http://localhost:5000/callback"

app = Flask(__name__)

# Global variable to store the access token
access_token = None

def exchange_code_for_token(code):
    """Exchange the authorization code for an access token."""
    url = 'https://accounts.spotify.com/api/token'
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    data = {
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': redirect_uri,
        'client_id': client_id,
        'client_secret': client_secret,
    }
    response = requests.post(url, headers=headers, data=urlencode(data))
    return response.json().get('access_token')

@app.route('/')
def hello_world():
    return 'Hello, visit /login to authorize.'

@app.route('/login')
def login():
    params = {
        "client_id": client_id,
        "response_type": "code",
        "redirect_uri": redirect_uri,
        "scope": "playlist-modify-public playlist-modify-private playlist-read-private",
    }
    url = f"https://accounts.spotify.com/authorize?{urlencode(params)}"
    return redirect(url)

@app.route('/callback')
def callback():
    global access_token
    code = request.args.get('code')
    if code:
        access_token = exchange_code_for_token(code)
        if access_token:
            return redirect('/playlists')
        else:
            return "Failed to obtain access token."
    else:
        return "Authorization failed."

@app.route('/playlists')
def playlists():
    """Fetch the user's playlists and store them in a DataFrame."""
    if access_token:
        url = 'https://api.spotify.com/v1/me/playlists'
        headers = {'Authorization': f'Bearer {access_token}'}
        response = requests.get(url, headers=headers)
        playlists = response.json().get('items', [])
        
        # Convert playlists to a DataFrame
        global df_playlists
        df_playlists = pd.DataFrame([(playlist['id'], playlist['name']) for playlist in playlists], columns=['ID', 'Name'])
        #print(df_playlists)  # Print DataFrame to console
        
        return "Playlists have been fetched. Check the console for the DataFrame."
    else:
        return "Access token is not available."
    

if __name__ == '__main__':
    webbrowser.open_new("http://localhost:5000/login")
    app.run(debug=False)
