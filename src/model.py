import json
import os
from pathlib import Path
from typing import TypedDict

import requests
from dotenv import load_dotenv
from requests.models import Response

from constants import API_BASE_URL, DOWNLOADS_DIR, GAME_DOMAIN
from mod import Mod


def get_api_key() -> str:
    load_dotenv(".env")
    api_key: str | None = os.getenv("NEXUS_API_KEY")
    if api_key is None:
        raise RuntimeError("Warning! Stored Nexus API Key is invalid!")
    return api_key


type ScopedId = str


class ModSearchResult(TypedDict):
    name: str
    scoped_id: ScopedId


def search_mods(query: str, verbose: bool = False) -> list[ModSearchResult]:
    search_header: dict[str, str] = {
        "apikey": get_api_key(),
        "Content-Type": "application/json",
    }
    mod_search_url: str = f"{API_BASE_URL}/v3/mods/search"

    mod_search_payload = {
        "query": f"{query}",
        "filters": {"games": [f"{GAME_DOMAIN}"]},
    }

    mod_search_resp: Response = requests.post(
        mod_search_url, headers=search_header, json=mod_search_payload
    )

    parsed_resp = mod_search_resp.json()

    parsed_mods: dict = parsed_resp["data"]["mods"]
    if verbose:
        print(
            "SEARCH RESULTS:\n------------------------------------\n",
            json.dumps(parsed_resp, sort_keys=True, indent=4),
        )

    search_results: list[ModSearchResult] = []
    for mod in parsed_mods:
        search_result: ModSearchResult = {
            "name": mod["name"],
            "scoped_id": mod["game_scoped_id"],
        }
        search_results.append(search_result)
        if verbose:
            print(mod["name"])
            print(mod["game_scoped_id"])

    return search_results


def get_mod_file(searchres: ModSearchResult, verbose=False) -> Mod:

    mod_name, scoped_id = searchres["name"], searchres["scoped_id"]
    # Gets main file
    list_files_url: str = f"{API_BASE_URL}/v1/games/{GAME_DOMAIN}/mods/{scoped_id}/files.json?category=main"

    list_files_resp: Response = requests.get(
        list_files_url, headers={"apikey": get_api_key()}
    )
    parsed_resp: dict = list_files_resp.json()
    if verbose:
        print(
            "FOUND MOD FILES\n-----------------------\n\n",
            json.dumps(parsed_resp, sort_keys=True, indent=4),
        )

    mod_version = parsed_resp["files"][0]["version"]
    file_id: str = parsed_resp["files"][0]["file_id"]

    download_links_url = f"{API_BASE_URL}/v1/games/{GAME_DOMAIN}/mods/{scoped_id}/files/{file_id}/download_link.json"
    list_files_resp: Response = requests.get(
        download_links_url, headers={"apikey": get_api_key()}
    )
    parsed_resp: dict = list_files_resp.json()
    if verbose:
        print(
            "FOUND DOWNLOAD LINKS\n-----------------------\n\n",
            json.dumps(parsed_resp, sort_keys=True, indent=4),
        )
    # Servers are sorted by performance metrics in desc order
    preferred_server_url = parsed_resp[0]["URI"]
    print(preferred_server_url)

    zip_resp: Response = requests.get(
        preferred_server_url, headers={"apikey": get_api_key()}
    )
    downloaded_file_path = Path.cwd() / f"{DOWNLOADS_DIR}/{mod_name}.zip"

    try:
        with downloaded_file_path.open("x"):
            downloaded_file_path.write_bytes(zip_resp.content)
    except FileExistsError:
        print(f"Mod '{mod_name}' already found in Downloads folder. Aborting...")

    return Mod(mod_name, scoped_id, mod_version)
