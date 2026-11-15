import json
import os
import pathlib

import requests
from dotenv import load_dotenv
from requests.models import Response

from constants import API_BASE_URL, DOWNLOADS_DIR, GAME_DOMAIN


def get_api_key() -> str:
    load_dotenv(".env")
    api_key: str | None = os.getenv("NEXUS_API_KEY")
    if api_key is None:
        raise RuntimeError("Warning! Stored Nexus API Key is invalid!")
    return api_key


def search_for_mods(query: str, verbose: bool = False):
    search_header: dict[str, str] = {
        "apikey": get_api_key(),
        "Content-Type": "application/json",
    }
    mod_search_url: str = f"{API_BASE_URL}/v3/mods/search"

    mod_search_payload = {
        "query": f"{query}",
        "filters": {"games": [f"{GAME_DOMAIN}"]},
    }
    mod_search_url: str = f"{API_BASE_URL}/v3/mods/search"

    mod_search_resp: Response = requests.post(
        mod_search_url, headers=search_header, json=mod_search_payload
    )

    parsed_resp = mod_search_resp.json()

    search_res: dict = parsed_resp["data"]["mods"]
    if verbose:
        print(
            "SEARCH RESULTS:\n------------------------------------\n",
            json.dumps(parsed_resp, sort_keys=True, indent=4),
        )
    for mod in search_res:
        if verbose:
            print(mod["name"])
            print(mod["id"])
            print(mod["game_scoped_id"])


# print(mod_uid)
# print(mod_scoped_id)

# Gets main file
# list_files_url: str = f"{API_BASE_URL}/v1/games/{GAME_DOMAIN}/mods/{mod_scoped_id}/files.json?category=main"

# list_files_resp = requests.get(list_files_url, headers=apikey_header)
# parsed_resp = list_files_resp.json()
# # print(json.dumps(parsed_resp,  sort_keys=True, indent=4))
# main_file_scoped_id = parsed_resp["files"][0]["file_id"]

# download_links_url = f"{API_BASE_URL}/v1/games/{GAME_DOMAIN}/mods/{mod_scoped_id}/files/{main_file_scoped_id}/download_link.json"
# list_files_resp = requests.get(download_links_url, headers=apikey_header)
# parsed_resp = list_files_resp.json()
# # print(json.dumps(parsed_resp,  sort_keys=True, indent=4))
# preferred_server_url = parsed_resp[0]["URI"]
# print(preferred_server_url)

# zip_resp = requests.get(preferred_server_url, headers=apikey_header)

# downloaded_file_path = pathlib.Path.cwd() / f"{DOWNLOADS_DIR}/{mod_name}.zip"

# try:
# with downloaded_file_path.open("x"):
#     downloaded_file_path.write_bytes(zip_resp.content)
# except FileExistsError:
# print(f"Mod '{mod_name}' already found in Downloads folder. Aborting...")


class SearchResult:
    def __init__(self, name: str, uid: str, scoped_id: str):
        self.name: str = name
        self.uid: str = uid
        self.scoped_id: str = scoped_id
