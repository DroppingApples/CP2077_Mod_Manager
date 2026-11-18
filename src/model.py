"""The Model class for Minimal Mod Manager (M3)."""

import json
import os
import zipfile
from pathlib import Path
from typing import TYPE_CHECKING, NewType, TypedDict

import requests
from dotenv import load_dotenv

if TYPE_CHECKING:
    from requests.models import Response

from constants import (
    API_BASE_URL,
    DOWNLOADS_DIR,
    GAME_DOMAIN,
    REQUEST_TIMEOUT,
)
from mod import Mod, TreeSet

ScopedId = NewType("ScopedId", str)


class SearchResult(TypedDict):
    """A search result for a mod on Nexus Mods."""

    name: str
    scoped_id: ScopedId


class Model:
    """The Model class for Minimal Mod Manager."""

    def __init__(self):
        """Initialize the Model class."""
        self.install_folder: str = ""

    def get_api_key(self) -> str:
        """Get the Nexus API key from the .env file."""
        load_dotenv(".env")
        api_key: str | None = os.getenv("NEXUS_API_KEY")
        if api_key is None:
            msg = "Warning! Stored Nexus API Key is invalid!"
            raise RuntimeError(
                msg,
            )
        return api_key

    def store_mod_archive(
        self,
        archive_contents: bytes,
        mod_name: str,
    ) -> None:
        """Store the mod archive in the Downloads directory."""
        archive_path = Path.cwd() / f"{DOWNLOADS_DIR}/{mod_name}.zip"

        with archive_path.open("x"):
            archive_path.write_bytes(archive_contents)

    def read_mod_archive(self, mod_name) -> TreeSet:
        """Read the mod archive and return a set of file paths."""
        mod_path = Path(DOWNLOADS_DIR) / Path(f"{mod_name}.zip")
        archive = zipfile.ZipFile(mod_path, "r")
        file_list: list[str] = archive.namelist()
        paths: TreeSet = TreeSet({Path(file) for file in file_list})
        return paths

    def search_mods(
        self,
        query: str,
        verbose: bool = False,
    ) -> list[SearchResult]:
        """Search for mods on Nexus Mods using provided query string."""
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
            mod_search_url,
            headers=search_header,
            json=mod_search_payload,
            timeout=REQUEST_TIMEOUT,
        )

        parsed_resp = mod_search_resp.json()

        parsed_mods: dict = parsed_resp["data"]["mods"]
        if verbose:
            print(
                "SEARCH RESULTS:\n----------------------------------\n",
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

    def get_mod_file_info(
        self,
        scoped_id: ScopedId,
        verbose=False,
    ) -> tuple[str, str]:
        """Get file_id and version of the mod with given scoped_id."""
        # This url query get "main" file!
        list_files_url: str = f"{API_BASE_URL}/v1/games/{GAME_DOMAIN}/\
mods/{scoped_id}/files.json?category=main"

        list_files_resp: Response = requests.get(
            list_files_url,
            headers={"apikey": self.get_api_key()},
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

    def get_cdn_url(
        self,
        scoped_id: str,
        file_id: str,
        verbose=False,
    ) -> str:
        """Get CDN URL for mod with given scoped_id and file_id."""
        download_links_url = f"{API_BASE_URL}/v1/games/{GAME_DOMAIN}/\
mods/{scoped_id}/files/{file_id}/download_link.json"
        list_files_resp: Response = requests.get(
            download_links_url,
            headers={"apikey": self.get_api_key()},
            timeout=REQUEST_TIMEOUT,
        )
        parsed_resp: dict = list_files_resp.json()
        if verbose:
            print(
                "FOUND DOWNLOAD LINKS\n-----------------------\n\n",
                json.dumps(parsed_resp, sort_keys=True, indent=4),
            )
        # Servers are sorted by performance metrics in desc order,
        # so pick first one
        cdn_server_url = parsed_resp[0]["URI"]
        if verbose:
            print("Preferred server URL:", cdn_server_url)

        return cdn_server_url

    def get_zip_file(self, cdn_server_url: str) -> bytes:
        """Get the zip file from the CDN server URL."""
        zip_resp: Response = requests.get(
            cdn_server_url,
            headers={"apikey": self.get_api_key()},
            timeout=REQUEST_TIMEOUT,
        )
        return zip_resp.content

    def download_mod(
        self,
        search_result: SearchResult,
        verbose=False,
    ) -> Mod:
        """Download mod from Nexus Mods using provided search result."""
        if verbose:
            print("Downloading mod", search_result["name"])
        mod_name, scoped_id = (
            search_result["name"],
            search_result["scoped_id"],
        )
        file_id, mod_version = self.get_mod_file_info(scoped_id)

        cdn_server_url = self.get_cdn_url(scoped_id, file_id)

        archive_contents: bytes = self.get_zip_file(cdn_server_url)

        self.store_mod_archive(archive_contents, mod_name)

        return Mod(mod_name, scoped_id, mod_version)
