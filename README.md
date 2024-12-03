# Sunshine Steam Game Importer

This Python script automatically imports your Steam games into Sunshine, a game streaming server, complete with grid images for each game.

## Features

- Automatically detects installed Steam games
- Fetches game names and grid images from SteamGridDB
- Updates Sunshine's apps.json with Steam games and their grid images
- Handles both new game entries and updates to existing entries

## Prerequisites

Before you begin, ensure you have met the following requirements:

- Python 3.7 or higher installed
- Sunshine installed and configured
- A SteamGridDB API key (get one from [SteamGridDB](https://www.steamgriddb.com/profile/preferences/api))

## Installation

1. Clone this repository or download the script.
2. Install the required Python libraries:

## Configuration

Before running the script, you need to configure a few paths and your API key:

1. Open the script in a text editor.
2. Update the following variables:
- `library_vdf_path`: Path to your Steam library VDF file
- `apps_json_path`: Path to your Sunshine apps.json file
- `grids_folder`: Path where you want to save the grid images
- `STEAMGRIDDB_API_KEY`: Your SteamGridDB API key

## Usage

To run the script:
1. Open a command prompt or terminal.
2. Navigate to the directory containing the script.
3. Run the script: python Sunshine-App-Automation.py

The script will:
1. Detect your installed Steam games
2. Fetch grid images for each game
3. Update Sunshine's apps.json file with the game information and grid image paths

## Troubleshooting

- If you encounter any "Access Denied" errors, try running the script with administrator privileges.
- Ensure your SteamGridDB API key is correct and has not expired.
- Check that all path variables in the script are correct for your system.

## Contributing

Contributions to improve the script are welcome. Please feel free to submit a Pull Request.

## Acknowledgements

- [Sunshine](https://github.com/LizardByte/Sunshine) for the game streaming server
- [SteamGridDB](https://www.steamgriddb.com/) for providing the grid images
