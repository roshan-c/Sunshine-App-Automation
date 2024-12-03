import os
import json
import vdf
import requests
import glob
from PIL import Image
import io
import subprocess
import time
import psutil

# Paths
library_vdf_path = r"C:\Program Files (x86)\Steam\steamapps\libraryfolders.vdf" #Change this to where your steam install is located
apps_json_path = r"C:\Users\<YourUsername>\AppData\Roaming\Sunshine\apps.json"  # Update to your correct path
grids_folder = r"C:\Sunshine grids"  # This should be the correct path for Sunshine grids on your computer
STEAMGRIDDB_API_KEY = "YOUR_API_KEY_HERE" #Make an account on steamgridDB, get the API key under account settings
steam_exe_path = r"D:\Steam\Steam.exe" #Put your steam exe here
sunshine_exe_path = r"C:\Program Files\Sunshine\sunshine.exe" Put your sunshine exe here


def restart_steam():
    print("Restarting Steam...")
    for proc in psutil.process_iter(['name']):
        if proc.name().lower() == 'steam.exe':
            proc.terminate()
            proc.wait()
    subprocess.Popen([steam_exe_path])
    time.sleep(10)  # Wait for Steam to start up

def restart_sunshine():
    print("Restarting Sunshine...")
    for proc in psutil.process_iter(['name']):
        if proc.name().lower() == 'sunshine.exe':
            proc.terminate()
            proc.wait()
    subprocess.Popen([sunshine_exe_path])

def get_game_name(app_id):
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
                return f"C:/Sunshine grids/{app_id}.png"
        return None
    except Exception as e:
        print(f"Error fetching grid for AppID {app_id}: {e}")
        return None

def get_sunshine_config(path):
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as file:
            config = json.load(file)
        print(f"Loaded Sunshine config with {len(config['apps'])} apps")
    else:
        config = {"env": "", "apps": []}
        print("Sunshine config not found, initializing empty config")
    return config

def save_sunshine_config(path, config):
    with open(path, 'w', encoding='utf-8') as file:
        json.dump(config, file, indent=4)
    print(f"Saved Sunshine config with {len(config['apps'])} apps")

# Restart Steam before processing
restart_steam()

print(f"Loading Steam library from {library_vdf_path}")
with open(library_vdf_path, 'r', encoding='utf-8') as file:
    steam_data = vdf.load(file)

print("Raw Steam library data:", steam_data)

installed_games = {}
for folder_data in steam_data.get('libraryfolders', {}).values():
    if "apps" in folder_data:
        for app_id, app_info in folder_data["apps"].items():
            game_name = get_game_name(app_id)
            if game_name:
                installed_games[app_id] = game_name

print(f"Found {len(installed_games)} installed games")
print("Installed games:", installed_games)

sunshine_config = get_sunshine_config(apps_json_path)

os.makedirs(grids_folder, exist_ok=True)

updated_apps = []
removed_games = []
existing_steam_apps = set()

for app in sunshine_config['apps']:
    if 'cmd' in app and app['cmd'].startswith('steam://rungameid/'):
        app_id = app['cmd'].split('/')[-1]
        if app_id in installed_games:
            updated_apps.append(app)
            existing_steam_apps.add(app_id)
        else:
            removed_games.append((app['name'], app_id))
            grid_path = app.get('image-path')
            if grid_path and os.path.exists(grid_path):
                os.remove(grid_path)
    else:
        updated_apps.append(app)

new_games = set(installed_games.keys()) - existing_steam_apps

print(f"Games to remove: {removed_games}")
print(f"New games to add: {[installed_games[app_id] for app_id in new_games]}")

for app_id in new_games:
    game_name = installed_games[app_id]
    grid_path = fetch_grid_from_steamgriddb(app_id)
    new_app = {
        "name": game_name,
        "cmd": f"steam://rungameid/{app_id}",
        "output": "",
        "detached": "",
        "elevated": "false",
        "hidden": "true",
        "wait-all": "true",
        "exit-timeout": "5",
        "image-path": grid_path or ""
    }
    updated_apps.append(new_app)
    print(f"Adding shortcut for newly installed game: {game_name}")

sunshine_config['apps'] = updated_apps

save_sunshine_config(apps_json_path, sunshine_config)
print("Sunshine apps.json update process completed")

# Restart Sunshine after processing
restart_sunshine()