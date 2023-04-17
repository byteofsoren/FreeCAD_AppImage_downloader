import requests
import os
import re
import stat
import yaml
import sys
from tqdm import tqdm


# Check if yaml file exists or not.
if not os.path.exists("config.yaml"):
    print("config.yaml did not exists.")
    print("create it by doing cp config.conf config.yaml")
    sys.exit(-1)

# Read yaml file
with open("config.yaml", 'r') as f:
    config = yaml.safe_load(f)
    pass


# Define the repository owner and repository name
# owner = 'realthunder'
# repo = 'FreeCAD'
# my_github_api_token='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'
owner  = config["github_repo"]["owner"]
repo  =  config["github_repo"]["repo"]
my_github_api_token = config["config"]["my_github_api_token"]


# Download directory
save_path = config["config"]["AppImagePath"]
# Define the API endpoint for getting the release information
api_url = f'https://api.github.com/repos/{owner}/{repo}/releases'

# Make a request to the API endpoint and get the release information
response = requests.get(api_url)
releases = response.json()

# Create a downloads directory if it does not exist
if not os.path.exists(save_path):
    if os.path.exists(save_path):
        os.rmdir(save_path)
    os.makedirs(save_path)

# Find the newest release that has an AppImage file
newest_release = None
newest_release_date = None
for release in releases:
    assets = [asset for asset in release['assets'] if asset['name'].endswith('.AppImage')]
    if assets:
        for asset in assets:
            asset_filename = asset['name']
            asset_date_match = re.search(r'(\d{8})', asset_filename)
            if asset_date_match:
                asset_date = asset_date_match.group(1)
                if not newest_release or asset_date > newest_release_date:
                    newest_release = release
                    newest_release_date = asset_date


# Download the AppImage file for the newest release
if newest_release:
    # remove symlink
    assets = [asset for asset in newest_release['assets'] if asset['name'].endswith('.AppImage')]
    if len(assets) > 1:
        print(f"Assets was to long suposed to find only one:\n{assets=}")
        sys.exit(-1)
    for asset in assets:
        asset_url = asset['url']
        asset_filename = asset['name']

        # Local directories
        download_path = os.path.join(save_path, asset_filename)
        absolute_path = os.path.abspath(download_path)

        # Remote connection
        headers = {'Authorization': f'token {my_github_api_token}'}
        asset_metadata_response = requests.get(asset_url, headers=headers)
        asset_metadata = asset_metadata_response.json()
        asset_download_url = asset_metadata['browser_download_url']
        response = requests.get(asset_download_url, headers=headers, stream=True)
        total_size = int(response.headers.get('content-length', 0))

        # Download the AppImage content.
        with open(download_path, 'wb') as f:
            for data in tqdm(response.iter_content(chunk_size=1024), total=total_size // 1024, unit='KB'):
                f.write(data)

        print(f'{asset_filename} downloaded successfully.')

        # Set execution rights to the AppImage file
        os.chmod(download_path, os.stat(download_path).st_mode | stat.S_IEXEC)

        # Create a symbolic link to the AppImage file
        if config["config"]["symlink"]["use"]:
            app_name = re.sub(r'\.AppImage$', '', asset_filename)
            link_path = os.path.expanduser(config["config"]["symlink"]["path"])
            print(f"{link_path=}")
            # Remove link if it existed
            if os.path.islink(link_path):
                print("Unilnk old version")
                os.unlink(link_path)
            # Create new link
            os.makedirs(os.path.dirname(link_path), exist_ok=True)
            os.symlink(absolute_path, link_path)
            print(f'Symbolic link created at {link_path}.')
        else:
            print(f"Symlink was not created because {config['config']['symlink']['use']=}")
else:
    print('No releases found with an AppImage file.')
