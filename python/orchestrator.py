# orchestrator.py

import requests
import json
import time
import os
from video_recorder import OBSRecorder
from video_stitcher import stitch_clips

# Load configuration from config.json
def load_config():
    with open('config.json', 'r') as f:
        return json.load(f)

config = load_config()
PLUGIN_URL = config['plugin_url']
OUTPUT_FOLDER = config['output_folder']
REPLAY_FOLDER = config['replay_folder']
OBS_CONFIG = config['obs']

def check_plugin_status():
    status_url = f"{PLUGIN_URL}/status"
    try:
        status_response = requests.get(status_url, timeout=5)
        status_response.raise_for_status()
        status_data = status_response.json()
        if status_data.get("status") != "ready":
            print(f"Plugin not ready. Status: {status_data.get('status')}")
            return False
        return True
    except requests.exceptions.RequestException as e:
        print(f"Error checking plugin status: {e}")
        return False

def load_replay(replay_path):
    """Sends a request to the BakkesMod plugin to load a replay."""
    if not check_plugin_status():
        return

    url = f"{PLUGIN_URL}/load_replay"
    headers = {'Content-Type': 'application/json'}
    data = {'path': replay_path}
    print(f"Sending load_replay request with data: {json.dumps(data)}")
    try:
        response = requests.post(url, headers=headers, data=json.dumps(data))
        response.raise_for_status()
        print(f"Successfully sent load_replay request for {replay_path}")
    except requests.exceptions.RequestException as e:
        print(f"Error sending load_replay request: {e}")

def get_highlights():
    """Sends a request to the BakkesMod plugin to get replay highlights."""
    if not check_plugin_status():
        return []

    url = f"{PLUGIN_URL}/replay/highlights"
    try:
        response = requests.get(url)
        response.raise_for_status()
        highlights = response.json()
        print(f"Received highlights: {highlights}")
        return highlights
    except requests.exceptions.RequestException as e:
        print(f"Error getting highlights: {e}")
        return []

def seek_replay(frame):
    """Sends a request to the BakkesMod plugin to seek to a specific frame in the replay."""
    if not check_plugin_status():
        return

    url = f"{PLUGIN_URL}/replay/seek"
    headers = {'Content-Type': 'application/json'}
    data = {'frame': frame}
    print(f"Sending seek request with data: {json.dumps(data)}")
    try:
        response = requests.post(url, headers=headers, data=json.dumps(data))
        response.raise_for_status()
        print(f"Successfully sent seek request to frame: {frame}")
    except requests.exceptions.RequestException as e:
        print(f"Error seeking replay: {e}")

def seek_replay_time(time_in_seconds):
    """Sends a request to the BakkesMod plugin to seek to a specific time in the replay."""
    if not check_plugin_status():
        return

    url = f"{PLUGIN_URL}/replay/seek_time"
    headers = {'Content-Type': 'application/json'}
    data = {'time': time_in_seconds}
    print(f"Sending seek_time request with data: {json.dumps(data)}")
    try:
        response = requests.post(url, headers=headers, data=json.dumps(data))
        response.raise_for_status()
        print(f"Successfully sent seek_time request to time: {time_in_seconds}")
    except requests.exceptions.RequestException as e:
        print(f"Error seeking replay by time: {e}")

def focus_game_window():
    """Sends a request to the BakkesMod plugin to focus the game window."""
    if not check_plugin_status():
        return

    url = f"{PLUGIN_URL}/focus"
    try:
        response = requests.post(url)
        response.raise_for_status()
        print("Successfully sent focus game window request.")
    except requests.exceptions.RequestException as e:
        print(f"Error focusing game window: {e}")

def set_camera_player(team, player):
    """Sends a request to the BakkesMod plugin to view a specific player in replay spectator mode."""
    if not check_plugin_status():
        return

    url = f"{PLUGIN_URL}/camera/player"
    headers = {'Content-Type': 'application/json'}
    data = {'team': team, 'player': player}
    print(f"Sending set_camera_player request with data: {json.dumps(data)}")
    try:
        response = requests.post(url, headers=headers, data=json.dumps(data))
        response.raise_for_status()
        print(f"Successfully sent set_camera_player request for team {team}, player {player}")
    except requests.exceptions.RequestException as e:
        print(f"Error setting camera player: {e}")

def set_camera_mode(mode):
    """Sends a request to the BakkesMod plugin to set the camera mode (fly, auto, default)."""
    if not check_plugin_status():
        return

    url = f"{PLUGIN_URL}/camera/mode"
    headers = {'Content-Type': 'application/json'}
    data = {'mode': mode}
    print(f"Sending set_camera_mode request with data: {json.dumps(data)}")
    try:
        response = requests.post(url, headers=headers, data=json.dumps(data))
        response.raise_for_status()
        print(f"Successfully sent set_camera_mode request to mode: {mode}")
    except requests.exceptions.RequestException as e:
        print(f"Error setting camera mode: {e}")

def set_camera_focus_actor(actor_string):
    """Sends a request to the BakkesMod plugin to set the camera focus actor."""
    if not check_plugin_status():
        return

    url = f"{PLUGIN_URL}/camera/focus_actor"
    headers = {'Content-Type': 'application/json'}
    data = {'actor_string': actor_string}
    print(f"Sending set_camera_focus_actor request with data: {json.dumps(data)}")
    try:
        response = requests.post(url, headers=headers, data=json.dumps(data))
        response.raise_for_status()
        print(f"Successfully sent set_camera_focus_actor request to actor: {actor_string}")
    except requests.exceptions.RequestException as e:
        print(f"Error setting camera focus actor: {e}")

def set_replay_slomo(slomo_value):
    """Sends a request to the BakkesMod plugin to set the replay speed (slomo)."""
    if not check_plugin_status():
        return

    url = f"{PLUGIN_URL}/replay/slomo"
    headers = {'Content-Type': 'application/json'}
    data = {'slomo': slomo_value}
    print(f"Sending set_replay_slomo request with data: {json.dumps(data)}")
    try:
        response = requests.post(url, headers=headers, data=json.dumps(data))
        response.raise_for_status()
        print(f"Successfully sent set_replay_slomo request to {slomo_value}")
    except requests.exceptions.RequestException as e:
        print(f"Error setting replay slomo: {e}")

def set_player_names_visibility(enabled):
    """Sends a request to the BakkesMod plugin to set the visibility of player names."""
    if not check_plugin_status():
        return

    url = f"{PLUGIN_URL}/replay/player_names"
    headers = {'Content-Type': 'application/json'}
    data = {'enabled': enabled}
    print(f"Sending set_player_names_visibility request with data: {json.dumps(data)}")
    try:
        response = requests.post(url, headers=headers, data=json.dumps(data))
        response.raise_for_status()
        print(f"Successfully sent set_player_names_visibility request to {enabled}")
    except requests.exceptions.RequestException as e:
        print(f"Error setting player names visibility: {e}")

def set_match_info_hud_visibility(enabled):
    """Sends a request to the BakkesMod plugin to set the visibility of the match info HUD."""
    if not check_plugin_status():
        return

    url = f"{PLUGIN_URL}/replay/match_info_hud"
    headers = {'Content-Type': 'application/json'}
    data = {'enabled': enabled}
    print(f"Sending set_match_info_hud_visibility request with data: {json.dumps(data)}")
    try:
        response = requests.post(url, headers=headers, data=json.dumps(data))
        response.raise_for_status()
        print(f"Successfully sent set_match_info_hud_visibility request to {enabled}")
    except requests.exceptions.RequestException as e:
        print(f"Error setting match info HUD visibility: {e}")

def set_replay_hud_visibility(enabled):
    """Sends a request to the BakkesMod plugin to set the visibility of the replay HUD."""
    if not check_plugin_status():
        return

    url = f"{PLUGIN_URL}/replay/replay_hud"
    headers = {'Content-Type': 'application/json'}
    data = {'enabled': enabled}
    print(f"Sending set_replay_hud_visibility request with data: {json.dumps(data)}")
    try:
        response = requests.post(url, headers=headers, data=json.dumps(data))
        response.raise_for_status()
        print(f"Successfully sent set_replay_hud_visibility request to {enabled}")
    except requests.exceptions.RequestException as e:
        print(f"Error setting replay HUD visibility: {e}")

def is_in_replay():
    """Sends a request to the BakkesMod plugin to check if the game is currently in a replay."""
    if not check_plugin_status():
        return False

    url = f"{PLUGIN_URL}/replay/is_in_replay"
    try:
        response = requests.get(url)
        response.raise_for_status()
        result = response.json()
        is_in_replay_status = result.get("is_in_replay", False)
        print(f"Is in replay: {is_in_replay_status}")
        return is_in_replay_status
    except requests.exceptions.RequestException as e:
        print(f"Error checking if in replay: {e}")
        return False

def get_replay_playback_info():
    """Gets playback info like current frame, fps, and time elapsed."""
    if not check_plugin_status():
        return None

    url = f"{PLUGIN_URL}/replay/playback_info"
    try:
        response = requests.get(url)
        response.raise_for_status()
        info = response.json()
        return info
    except requests.exceptions.RequestException as e:
        print(f"Error getting playback info: {e}")
        return None

def get_player_map():
    """Gets a map of player names to their team and index."""
    if not check_plugin_status():
        return None

    url = f"{PLUGIN_URL}/replay/player_map"
    try:
        response = requests.get(url)
        response.raise_for_status()
        player_map = response.json()
        print(f"Received player map: {player_map}")
        return player_map
    except requests.exceptions.RequestException as e:
        print(f"Error getting player map: {e}")
        return None

def set_player_pov(player_name):
    """Sets the camera to the POV of the specified player by name."""
    player_map = get_player_map()
    if player_map and player_name in player_map:
        player_info = player_map[player_name]
        set_camera_player(player_info['team'], player_info['index'])
    else:
        print(f"Player '{player_name}' not found in player map.")
    
def pause_replay():
    set_replay_slomo(0.0)

def play_replay():
    set_replay_slomo(1.0)


if __name__ == "__main__":
    clip_paths = []
    temp_clip_dir = os.path.join(OUTPUT_FOLDER, "temp_clips")
    os.makedirs(temp_clip_dir, exist_ok=True)

    # Example usage with OBS
    example_replay_path = "C:\\Users\\kyles\\Downloads\\f1722816-9180-43cc-9d87-0a2ad7b45e10.replay"
    
    # Use context manager to automatically connect/disconnect
    with OBSRecorder(os.path.join(temp_clip_dir, "highlight_1.mp4"), OBS_CONFIG) as recorder:
        if not recorder.is_connected:
            print("Failed to connect to OBS. Make sure OBS is running.")
            exit(1)
        
        # Load replay and wait for it to be ready
        load_replay(example_replay_path)
        focus_game_window()
        
        while not is_in_replay():
            print("Waiting for replay to load...")
            time.sleep(0.5)
        
        # Configure replay view
        set_replay_hud_visibility(False)
        time.sleep(1)
        set_player_pov("Onesiee.")
        
        # Seek to desired time
        pause_replay()
        seek_replay_time(210)
        play_replay()
        time.sleep(1)
        pause_replay()
        
        # --- Start Recording ---
        print("Starting OBS recording for clip 1...")
        recorder.start_recording()
        play_replay()
        
        # Wait for clip duration
        time_elapsed = 0
        target_time = 211 + 9
        while time_elapsed < target_time:
            info = get_replay_playback_info()
            if info:
                time_elapsed = info.get('time_elapsed', 0)
            time.sleep(0.1)
        
        # --- Stop Recording ---
        recorder.stop_recording()
        print("Stopped recording for clip 1.")
        
        # Get the actual recorded file and rename it if needed
        recorded_file = recorder.get_last_recording_path()
        if recorded_file:
            clip_paths.append(recorded_file)
        
        # Record another clip
        pause_replay()
        seek_replay_time(239)
        play_replay()
        time.sleep(0.2)
        set_player_pov("Not IHung_")
        
        # You can continue recording more clips here...
    
    print("\nRecording session complete!")
    print(f"Recorded {len(clip_paths)} clip(s)")
    
    # Optionally stitch clips together
    # if clip_paths:
    #     final_video_name = f"{os.path.splitext(os.path.basename(example_replay_path))[0]}_highlights.mp4"
    #     final_video_path = os.path.join(OUTPUT_FOLDER, final_video_name)
    #     print("Stitching clips together...")
    #     stitch_clips(clip_paths, final_video_path)
    #     print(f"Successfully created highlight reel: {final_video_path}")