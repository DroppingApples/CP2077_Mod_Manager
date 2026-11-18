import json
import os
import zipfile
from pathlib import Path
from typing import NewType, TypedDict

import requests
from dotenv import load_dotenv
from requests.models import Response

from constants import API_BASE_URL, DOWNLOADS_DIR, GAME_DOMAIN
from mod import Mod, TreeSet

ScopedId = NewType("ScopedId", str)


class SearchResult(TypedDict):
    name: str
    scoped_id: ScopedId


class Model:
    """The Model class for Minimal Mod Manager"""

    def __init__(self, install_folder: str = ""):
        self.install_folder: str = ""

    def get_api_key(self) -> str:
        load_dotenv(".env")
        api_key: str | None = os.getenv("NEXUS_API_KEY")
        if api_key is None:
            raise RuntimeError("Warning! Stored Nexus API Key is invalid!")
        return api_key

    def store_mod_archive(self, archive_contents: bytes, mod_name: str) -> None:
        archive_path = Path.cwd() / f"{DOWNLOADS_DIR}/{mod_name}.zip"

        with archive_path.open("x"):
            archive_path.write_bytes(archive_contents)

    def read_mod_archive(self, mod_name) -> TreeSet:
        mod_path = Path(DOWNLOADS_DIR) / Path(f"{mod_name}.zip")
        archive = zipfile.ZipFile(mod_path, "r")
        file_list: list[str] = archive.namelist()
        paths: TreeSet = TreeSet({Path(file) for file in file_list})
        return paths

    def search_mods(self, query: str, verbose: bool = False) -> list[SearchResult]:
        search_header: dict[str, str] = {
            "apikey": self.get_api_key(),
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

        search_results: list[SearchResult] = []
        for mod in parsed_mods:
            search_result: SearchResult = {
                "name": mod["name"],
                "scoped_id": mod["game_scoped_id"],
            }
            search_results.append(search_result)
            if verbose:
                print(
                    "Found mod",
                    mod["name"],
                    "with game_scoped_id",
                    mod["game_scoped_id"],
                )

        return search_results

    def get_mod_file_info(self, scoped_id: ScopedId, verbose=False) -> tuple[str, str]:
        # This url query get "main" file!
        list_files_url: str = f"{API_BASE_URL}/v1/games/{GAME_DOMAIN}/mods/{scoped_id}/files.json?category=main"

        list_files_resp: Response = requests.get(
            list_files_url, headers={"apikey": self.get_api_key()}
        )
        parsed_resp: dict = list_files_resp.json()
        if verbose:
            print(
                "FOUND MOD FILES\n-----------------------\n\n",
                json.dumps(parsed_resp, sort_keys=True, indent=4),
            )

        mod_version = parsed_resp["files"][0]["version"]
        file_id: str = parsed_resp["files"][0]["file_id"]
        return file_id, mod_version

    def get_CDN_url(self, scoped_id: str, file_id: str, verbose=False) -> str:
        download_links_url = f"{API_BASE_URL}/v1/games/{GAME_DOMAIN}/mods/{scoped_id}/files/{file_id}/download_link.json"
        list_files_resp: Response = requests.get(
            download_links_url, headers={"apikey": self.get_api_key()}
        )
        parsed_resp: dict = list_files_resp.json()
        if verbose:
            print(
                "FOUND DOWNLOAD LINKS\n-----------------------\n\n",
                json.dumps(parsed_resp, sort_keys=True, indent=4),
            )
        # Servers are sorted by performance metrics in desc order, so pick first one
        CDN_server_url = parsed_resp[0]["URI"]
        if verbose:
            print("Preferred server URL:", CDN_server_url)

        return CDN_server_url

    def get_zip_file(self, CDN_server_url: str) -> bytes:
        zip_resp: Response = requests.get(
            CDN_server_url, headers={"apikey": self.get_api_key()}
        )
        return zip_resp.content

    def download_mod(self, search_result: SearchResult, verbose=False) -> Mod:
        if verbose:
            print("Downloading mod", search_result["name"])
        mod_name, scoped_id = search_result["name"], search_result["scoped_id"]
        file_id, mod_version = self.get_mod_file_info(scoped_id)

        CDN_server_url = self.get_CDN_url(scoped_id, file_id)

        archive_contents: bytes = self.get_zip_file(CDN_server_url)

        self.store_mod_archive(archive_contents, mod_name)

        return Mod(mod_name, scoped_id, mod_version)
