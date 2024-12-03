import os
import json
import vdf
import requests
import glob
from PIL import Image
import io


library_vdf_path = r"D:/Steam/steamapps/libraryfolders.vdf"
apps_json_path = r"C:/Program Files/Sunshine/config/apps.json"
STEAMGRIDDB_API_KEY = "0c81c015dcb00272c18ae67431dc7953"
grids_folder = r"C:\Sunshine grids"

def get_game_name(app_id):
    """Fetch game name from Steam API."""
    try:
        url = f"https://store.steampowered.com/api/appdetails?appids={app_id}"
        response = requests.get(url)
        data = response.json()
        if data[str(app_id)]['success']:
            return data[str(app_id)]['data']['name']
        return None
    except Exception as e:
        print(f"Error fetching name for AppID {app_id}: {e}")
        return None

def fetch_grid_from_steamgriddb(app_id):
    """Fetch game grid from SteamGridDB and save as PNG."""
    try:
        url = f"https://www.steamgriddb.com/api/v2/grids/steam/{app_id}"
        headers = {"Authorization": f"Bearer {STEAMGRIDDB_API_KEY}"}
        response = requests.get(url, headers=headers)
        data = response.json()
        if "data" in data and len(data["data"]) > 0:
            grid_url = data["data"][0]["url"]
            grid_response = requests.get(grid_url)
            if grid_response.status_code == 200:
                image = Image.open(io.BytesIO(grid_response.content))
                grid_path = os.path.join(grids_folder, f"{app_id}.png")
                image.save(grid_path, "PNG")
                return f"C:/Sunshine grids/{app_id}.png"  # Return the correct path for Sunshine
        return None
    except Exception as e:
        print(f"Error fetching grid for AppID {app_id}: {e}")
        return None

def get_sunshine_config(path):
    """Load Sunshine apps.json and ensure it's valid."""
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as file:
            config = json.load(file)
    else:
        config = {"env": "", "apps": []}  # Initialize with correct structure
    return config

def save_sunshine_config(path, config):
    """Save Sunshine apps.json."""
    with open(path, 'w', encoding='utf-8') as file:
        json.dump(config, file, indent=4)

# Load Steam library info
with open(library_vdf_path, 'r', encoding='utf-8') as file:
    steam_data = vdf.load(file)

# Fetch installed games
installed_games = []
for folder_data in steam_data.get('libraryfolders', {}).values():
    if "apps" in folder_data:
        for app_id in folder_data["apps"]:
            game_name = get_game_name(app_id)
            if game_name:
                installed_games.append({
                    "app_id": app_id,
                    "name": game_name
                })

# Load Sunshine apps.json
sunshine_config = get_sunshine_config(apps_json_path)

# Ensure grids folder exists
os.makedirs(grids_folder, exist_ok=True)

# Update or add Steam games to Sunshine apps.json
for game in installed_games:
    # Check if game already exists
    existing_app = next((app for app in sunshine_config['apps'] if app['name'] == game["name"]), None)
    
    # Fetch grid
    grid_path = fetch_grid_from_steamgriddb(game["app_id"])
    
    if existing_app:
        # Update existing entry
        existing_app.update({
            "cmd": f"steam://rungameid/{game['app_id']}",
            "output": "",
            "detached": "",
            "elevated": "false",
            "hidden": "true",
            "wait-all": "true",
            "exit-timeout": "5",
            "image-path": grid_path or existing_app.get('image-path', '')
        })
    else:
        # Create a new app entry
        new_app = {
            "name": game["name"],
            "cmd": f"steam://rungameid/{game['app_id']}",
            "output": "",
            "detached": "",
            "elevated": "false",
            "hidden": "true",
            "wait-all": "true",
            "exit-timeout": "5",
            "image-path": grid_path or ""
        }
        sunshine_config['apps'].append(new_app)

# Save updated apps.json
save_sunshine_config(apps_json_path, sunshine_config)
print("Sunshine apps.json updated!")