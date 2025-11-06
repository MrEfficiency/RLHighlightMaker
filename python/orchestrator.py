# orchestrator.py

import requests
import json
import time

# Load configuration from config.json
def load_config():
    with open('config.json', 'r') as f:
        return json.load(f)

config = load_config()
PLUGIN_URL = config['plugin_url']

def check_plugin_status():
    status_url = f"{PLUGIN_URL}/status"
    try:
        status_response = requests.get(status_url, timeout=5)
        status_response.raise_for_status()
        status_data = status_response.json()
        if status_data.get("status") != "ready":
            print(f"Plugin not ready. Status: {status_data.get("status")}")
            return False
        print("Plugin is ready.")
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
        response.raise_for_status()  # Raise an exception for HTTP errors
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
        highlights = response.json().get("highlights", [])
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
    
def pause_replay():
    set_replay_slomo(0.0)

def play_replay():
    set_replay_slomo(1.0)



if __name__ == "__main__":
    # Example usage (replace with actual replay path)
    example_replay_path = "C:\\Users\\kyles\\Downloads\\f1722816-9180-43cc-9d87-0a2ad7b45e10.replay" # Placeholder
    load_replay(example_replay_path)
    focus_game_window()
    while not is_in_replay():
        print("Waiting for replay to load...")
        time.sleep(0.5)
    #set_player_names_visibility(False) # Example: Hide player names
    #set_match_info_hud_visibility(False) # Example: Hide match info HUD
    set_replay_hud_visibility(False) # Example: Disable replay HUD
    time.sleep(1)
    set_camera_player(0, 0) # Example: View player 0 on team 0
    #set_camera_mode("default") # Example: Set camera mode to fly
    time.sleep(2)  # Wait for 2 seconds to ensure the replay is loaded
    seek_replay(2000)
    #control_playback("pause")
    #set_camera_player(0, 0) # Example: View player 0 on team 0
    time.sleep(1)
    #set_camera_mode("default") # Example: Set camera mode to fly
    #time.sleep(1)
    #set_camera_focus_actor("ball") # Example: Focus camera on the ball
    pause_replay()
    time.sleep(1)
    seek_replay(5000)
    play_replay()
