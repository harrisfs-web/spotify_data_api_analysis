from flask import Flask, request, redirect, render_template_string
import webbrowser
import os
from urllib.parse import urlencode
import requests
import pandas as pd
from dotenv import load_dotenv
import plotly.express as px
import plotly.io as pio
import plotly.graph_objects as go


load_dotenv()

client_id = os.getenv("client_id")
client_secret = os.getenv("client_secret")
redirect_uri = "http://localhost:5000/callback"

app = Flask(__name__)

# Global variable to store the access token
access_token = None
df_artists = pd.DataFrame(columns=['Artist Name', 'Track Name'])  # Initial empty DataFrame for artists

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
    
def fetch_artists_for_playlists(df_playlists):
    global df_artists, df_track_info
    if not df_playlists.empty:
        artist_data = []
        track_info = []
        for i in range(len(df_playlists)):
            playlist_id = df_playlists.iloc[i]['ID']  # Get the first playlist ID
            next_url = f'https://api.spotify.com/v1/playlists/{playlist_id}/tracks'
            headers = {'Authorization': f'Bearer {access_token}'}
            
            
            while next_url:
                response = requests.get(next_url, headers=headers)
                json_response = response.json()
                tracks = json_response.get('items', [])
                next_url = json_response.get('next')  # URL for the next page
    
                for track_item in tracks:
                    track = track_item.get('track', {})
                    track_name = track.get('name', 'Unknown Track')
                    artists = track.get('artists', [])
                    duration = track['duration_ms']
                    popularity = track['popularity']
                    release_date = track['album']['release_date']
                    track_info.append([track_name,duration,popularity,release_date])
                    for artist in artists:
                        artist_data.append([artist['name'], track_name])

        df_artists = pd.DataFrame(artist_data, columns=['Artist Name', 'Track Name'])
        df_track_info = pd.DataFrame(track_info, columns=['Track Name','Duration','Popularity','Release Date'])


@app.route('/playlists')
def playlists():
    """Fetch the user's playlists and store them in a DataFrame, then fetch artists for the first playlist."""
    global df_playlists, df_artists,df_artist_frequencies
    if access_token:
        url = 'https://api.spotify.com/v1/me/playlists'
        headers = {'Authorization': f'Bearer {access_token}'}
        response = requests.get(url, headers=headers)
        playlists = response.json().get('items', [])
        
        # Convert playlists to a DataFrame
        df_playlists = pd.DataFrame([(playlist['id'], playlist['name']) for playlist in playlists], columns=['ID', 'Name'])

        if not df_playlists.empty:
            fetch_artists_for_playlists(df_playlists)
            artist_frequencies = df_artists['Artist Name'].value_counts().reset_index()
            artist_frequencies.columns = ['Artist Name', 'Frequency']
            
            # Save the result in a new DataFrame
            df_artist_frequencies = pd.DataFrame(artist_frequencies)
            
        
        return redirect('/visualize_artist_frequencies')
    else:
        return "Access token is not available."


@app.route('/visualize_artist_frequencies')
def visualize_artist_frequencies():
    global df_artist_frequencies, df_track_info
    if df_artist_frequencies is not None and df_track_info is not None:
        # Artist Frequency Graph
        fig1 = px.bar(df_artist_frequencies, x='Artist Name', y='Frequency', title='Artist Frequency in Playlist')

        
        # Table for Top 10 Artists
        top_artists = df_artist_frequencies.head(10)
        fig_table = go.Figure(data=[go.Table(
            header=dict(values=['Artist Name', 'Frequency']),
            cells=dict(values=[top_artists['Artist Name'], top_artists['Frequency']]))
        ])
        fig_table.update_layout(
        title_text='Top 10 Artists by Total Appearences',  # Title for the table
        title_x=0.5)
        
        table_html = pio.to_html(fig_table, full_html=False)

        # Track Release Date Graph
        df_track_info['Release Date'] = pd.to_datetime(df_track_info['Release Date'])
        df_track_info['Year'] = df_track_info['Release Date'].dt.year
        fig2 = px.violin(df_track_info, y='Year', box=True, points="all", title='Track Release Years in Playlist')

        # Popularity Distribution Graph
        fig3 = px.histogram(df_track_info, x='Popularity', nbins=30, title='Track Popularity Distribution')
        
        # Duration Distribution Graph
        df_track_info['Duration Minutes'] = df_track_info['Duration'] / 60000  # Convert ms to minutes for readability
        fig4 = px.histogram(df_track_info, x='Duration Minutes', nbins=30, title='Track Duration Distribution (Minutes)')

        
        # No need to set explicit height in update_layout if we want it to autosize
        fig1.update_layout(autosize=True)
        fig2.update_layout(autosize=True)
        fig3.update_layout(autosize=True)
        fig4.update_layout(autosize=True)
        

        # Convert your Plotly figures to HTML with the proper config
        graph_html1 = pio.to_html(fig1, full_html=False, config={'responsive': True})
        graph_html2 = pio.to_html(fig2, full_html=False, config={'responsive': True})
        graph_html3 = pio.to_html(fig3, full_html=False, config={'responsive': True})
        graph_html4 = pio.to_html(fig4, full_html=False, config={'responsive': True}) 
        
        # Update your combined HTML template
        combined_html = f"""
        <html>
            <head>
                <title>Spotify Playlist Analysis</title>
                <style>
                    body, html {{
                        margin: 0;
                        padding: 0;
                        height: 100%;
                        overflow: hidden;
                    }}
                    .plot-container {{
                        display: flex;
                        flex-wrap: nowrap;
                        align-items: stretch;
                    }}
                    .plot {{
                        flex: 1;
                        display: flex;
                        flex-direction: column;
                    }}
                    .plot-graph {{
                        flex-basis: 70%;
                    }}
                    .plot-table {{
                        flex-basis: 30%;
                    }}
                    .flex-item {{
                        flex-basis: 33%;
                    }}
                    iframe {{
                        border: none;
                        width: 100%;
                        height: 100%;
                    }}
                </style>
            </head>
            <body>
                <div class="plot-container" style="height: 50vh;"> <!-- For top half -->
                    <div class="plot plot-graph" >{graph_html1}</div>
                    <div class="plot plot-table">{table_html}</div>
                </div>
                <div class="plot-container" style="height: 50vh;"> <!-- For bottom half -->
                    <div class="flex-item" style="flex-basis: 33%;">{graph_html2}</div>
                    <div class="flex-item" style="flex-basis: 33%;">{graph_html3}</div>
                    <div class="flex-item" style="flex-basis: 33%;">{graph_html4}</div>
                </div>
            </body>
        </html>
        """

        
        return render_template_string(combined_html)
    else:
        return "Data is not available for visualization."


if __name__ == '__main__':
    webbrowser.open_new("http://localhost:5000/login")
    app.run(debug=False)
    
