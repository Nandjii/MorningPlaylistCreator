#!/usr/bin/env python3
import os
import socket
import random
from spotipy import *
import spotipy.exceptions
from dotenv import load_dotenv

# Load secret .env file
load_dotenv()

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
hostname = socket.gethostname()

s.bind((socket.gethostname(), 8023))
s.listen(5)

#variables
USERNAME = os.getenv('NAME')
SCOPE = os.getenv('SCOPE')
SP_CLIENT_ID = os.getenv('SP_CLIENT_ID')
SP_CLIENT_PASS = os.getenv('SP_CLIENT_PASS')
SP_REDIRECT_URI = os.getenv('SP_REDIRECT_URI')
DEVICE = os.getenv('DEVICE')
playlist_morning_routine = os.getenv('playlist_morning_routine')
playlist_inspiration = os.getenv('playlist_inspiration')
inspiration_tracks = []
inspiration_artists = []
inspiration_genres = []
inspiration_energy = []
inspiration_liveness = []


def play_music(speaker, playlist, vol):
    sp.transfer_playback(device_id=speaker)
    sp.volume(vol, device_id=speaker)
    sp.start_playback(device_id=speaker, uris=playlist)


def get_device_id(devices):
    for device in devices["devices"]:
        if device["name"] == DEVICE:
            device_id = device["id"]
            return device_id


# # authentication
sp = Spotify(auth_manager=SpotifyOAuth(scope=SCOPE,
                                       client_id=SP_CLIENT_ID,
                                       client_secret=SP_CLIENT_PASS,
                                       redirect_uri=SP_REDIRECT_URI,
                                       open_browser=False,  
                                       cache_path=".cache",  
                                       show_dialog=True))

# remove exiting playlist
morning = sp.playlist_items(playlist_id=playlist_morning_routine)["items"]
morning_id = [t["track"]["id"] for t in morning]
sp.playlist_remove_all_occurrences_of_items(playlist_id=playlist_morning_routine, items=morning_id,)

# select tracks for recommendations
morning = sp.playlist_items(playlist_id=playlist_inspiration)["items"]
chille_vibe = random.choices(morning, k=2)

# determine choice track features
for track in chille_vibe:
    artist = track["track"]["album"]["artists"][0]["id"]
    inspiration_artists.append(artist)

    track_id = track["track"]["id"]
    inspiration_tracks.append(track_id)

    genres = sp.artist(track["track"]["album"]["artists"][0]["id"])["genres"]
    print(genres)
    if len(genres) > 1:
        inspiration_genres = random.choices(genres, k=1)
    else:
        inspiration_genres = genres

    energy = float(sp.audio_features(track["track"]["id"])[0]["energy"])
    inspiration_energy.append(energy)

    liveness = float(sp.audio_features(track["track"]["id"])[0]["liveness"])
    inspiration_liveness.append(liveness)
#
# Get new tracks and add them to morning routine playlist
recommendations = sp.recommendations(seed_genres=inspiration_genres,
                                     seed_artists=inspiration_artists,
                                     seed_tracks=inspiration_tracks,
                                     seed_energy=inspiration_energy,
                                     seed_liveness=inspiration_liveness
                                     )

new_playlist = [track["id"] for track in recommendations["tracks"]]
sp.playlist_add_items(playlist_id=playlist_morning_routine, items=new_playlist)
sp.playlist_add_items(playlist_id=playlist_morning_routine, items=inspiration_tracks)
#
# Get track URIS and select Pioneer device and start music
playlist_uris = sp.playlist_items(playlist_id=playlist_morning_routine)["items"]
playlist_uri = [uri["track"]["uri"] for uri in playlist_uris]

devices_dict = sp.devices()
device = get_device_id(devices_dict)

volume = 40
try:
    play_music(device, playlist_uri, volume)
except spotipy.exceptions.SpotifyException:
    sp.transfer_playback(device_id=device)
    sp.start_playback(device_id=device, uris=playlist_uri)
else:
    play_music(device, playlist_uri, volume)

