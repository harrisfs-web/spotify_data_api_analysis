# Spotify Playlist Artist Fetcher

This Python script automates the process of fetching artists from the first playlist of a Spotify user's account and analyzing the frequency of each artist's appearance in that playlist. It utilizes the Spotify Web API to authenticate, access user playlists, and extract artist data.

Of course there are many adjustments that can be done in the code and report to give more insights and improve the UI/UX but the goal is to demonstrate the capabilities of combining python, APIs, plotting tools to get insights from user data

## Contents

1. spotify_playlist_analysis script which authenticates user, fetches all playlists, artists and songs and creates a one-page report with insights about the user's song data
2. spotify_auth_code script as a standalone authentication script to gain access through Spotify's API
3. spotify_get_playlists script to save all playlists of the user which can be used for further exporation

## Playlist Analysis Rerport

![alt text](<Playlist Analysis Report.png>)

## Features

- OAuth 2.0 Authentication with Spotify.
- Fetches all tracks from the user's first playlist.
- Extracts artist names from the tracks.
- Calculates the frequency of each artist's appearance in the playlist.
- Stores artist frequencies in a pandas DataFrame.

## Prerequisites

Before running the script, you need to complete some setup steps on the Spotify Developer Dashboard and in your local environment.

### Spotify Developer Account Setup

1. **Create a Spotify Developer Account:**
   - Visit [Spotify Developer Dashboard](https://developer.spotify.com/dashboard/) and log in with your Spotify account.
   - Accept the Developer Terms of Service to activate your Developer account.

2. **Register Your Application:**
   - Click on `Create an App`.
   - Fill in the `Name` and `Description` for your application and agree to the terms.
   - Click `Create`. You'll be redirected to your application's dashboard.

3. **Note Your Client ID and Client Secret:**
   - On your application's dashboard, you'll find the `Client ID` and `Client Secret`.
   - These are important for your script to authenticate with Spotify's API.

4. **Set Redirect URI:**
   - In the application settings, find the `Redirect URIs` section.
   - Add `http://localhost:5000/callback` as a new Redirect URI.
   - Save your changes.

### Local Environment Setup

1. **Environment Variables:**
   - Store your `Client ID` and `Client Secret` in a `.env` file in your project directory:
     ```plaintext
     client_id=YOUR_CLIENT_ID_HERE
     client_secret=YOUR_CLIENT_SECRET_HERE
     ```
   - Replace `YOUR_CLIENT_ID_HERE` and `YOUR_CLIENT_SECRET_HERE` with the actual values from your Spotify application.

2. **Dependencies:**
   - The script requires Python 3 and the following packages: `flask`, `requests`, `pandas`, `python-dotenv`, and `webbrowser`.
   - Install the required packages using pip:
     ```bash
     pip install Flask requests pandas python-dotenv
     ```

## Running the Script

Simply running the playlist_analysis python script should redirect you to the browser and after authentication and data load the report should be visible