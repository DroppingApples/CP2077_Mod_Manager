"""The Model module for Minimal Mod Manager (M3)."""

import os
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
from mod import Mod

ScopedId = NewType("ScopedId", str)


class SearchResult(TypedDict):
    """A search result for a mod on Nexus Mods."""

    name: str
    scoped_id: ScopedId


class Model:
    """
    The Model class for Minimal Mod Manager.

    Attributes
    ----------
    install_folder: str
        The absolute path to the root game folder.
    mods: list of Mod
        List of mod objects to manage as used by controller.

    """

    def __init__(self):
        """Initialize Model class."""
        self.install_folder: str = ""
        self.mods: list[Mod] = []
        self.populate_mods()

    def get_api_key(self) -> str:
        """
        Get Nexus API key from .env file.

        Returns
        -------
        str
            The API key used for auth.

        """
        load_dotenv(".env")
        api_key: str | None = os.getenv("NEXUS_API_KEY")
        if api_key is None:
            msg = "Warning! Stored Nexus API Key is invalid!"
            raise RuntimeError(
                msg,
            )
        return api_key

    def populate_mods(self) -> None:
        """Read Download folder and append mods to model.mods member."""
        for file_path in Path(DOWNLOADS_DIR).iterdir():
            # Awful hack!
            # "Downloads/"" and ".zip" are stripped from path
            mod_name, version = str(file_path.with_suffix(""))[
                10:
            ].rsplit(" V", 1)
            self.mods.append(
                Mod(mod_name, version),
            )

    def store_mod_archive(
        self,
        archive_contents: bytes,
        mod_name: str,
        mod_version: str,
    ) -> None:
        """Store mod archive in the Downloads directory."""
        archive_path = (
            Path.cwd()
            / f"{DOWNLOADS_DIR}/{mod_name} V{mod_version}.zip"
        )
        with archive_path.open("x"):
            archive_path.write_bytes(archive_contents)

    def search_mods(
        self,
        query: str,
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

        search_results: list[SearchResult] = []
        for mod in parsed_mods:
            search_result: SearchResult = {
                "name": mod["name"],
                "scoped_id": mod["game_scoped_id"],
            }
            search_results.append(search_result)

        return search_results

    def get_mod_file_info(
        self,
        scoped_id: ScopedId,
    ) -> tuple[str, str]:
        """
        Get file_id and version of mod with given scoped_id.

        Parameters
        ----------
        scoped_id : ScopedId
            Scoped Id string for game scoped mod id.

        Returns
        -------
        tuple of str, str:
            The unique file id and version number of latest file.

        """
        # This url query get "main" file!
        list_files_url: str = f"{API_BASE_URL}/v1/games/{GAME_DOMAIN}/\
mods/{scoped_id}/files.json?category=main"

        list_files_resp: Response = requests.get(
            list_files_url,
            headers={"apikey": self.get_api_key()},
            timeout=REQUEST_TIMEOUT,
        )
        parsed_resp: dict = list_files_resp.json()
        mod_version = parsed_resp["files"][0]["version"]
        file_id: str = parsed_resp["files"][0]["file_id"]
        return file_id, mod_version

    def get_cdn_url(self, scoped_id: ScopedId, file_id: str) -> str:
        """
        Get CDN URL for mod with given scoped_id and file_id.

        Parameters
        ----------
        scoped_id : ScopedId
            Scoped Id type string for game scoped mod id.

        file_id : str
            A unique file id integer held as string.

        Returns
        -------
        str
            Http URL to CDN server hosting the file.

        """
        download_links_url = f"{API_BASE_URL}/v1/games/{GAME_DOMAIN}/\
mods/{scoped_id}/files/{file_id}/download_link.json"
        list_files_resp: Response = requests.get(
            download_links_url,
            headers={"apikey": self.get_api_key()},
            timeout=REQUEST_TIMEOUT,
        )
        parsed_resp: dict = list_files_resp.json()
        # Servers are sorted by performance metrics in desc order,
        # so [0] picks probable best choice.
        return parsed_resp[0]["URI"]

    def get_zip_file(self, cdn_server_url: str) -> bytes:
        """
        Get the zip file from the CDN server URL.

        Parameters
        ----------
        cdn_server_url : str
            HTTP URL to mod arhcive file hosted on CDN server.

        Returns
        -------
        bytes:
            The zip binary contents of HTTP response.

        """
        zip_resp: Response = requests.get(
            cdn_server_url,
            headers={"apikey": self.get_api_key()},
            timeout=REQUEST_TIMEOUT,
        )
        return zip_resp.content

    def download_mod(self, search_result: SearchResult) -> Mod:
        """
        Download mod from Nexus Mods using provided search result.

        Parameters
        ----------
        search_result : SearchResult
            SearchResult tuple holding mod name and scoped id.

        Returns
        -------
        Mod:
            New object containing metadata about downloaded mod.
        """
        mod_name, scoped_id = (
            search_result["name"],
            search_result["scoped_id"],
        )
        file_id, mod_version = self.get_mod_file_info(scoped_id)

        cdn_server_url = self.get_cdn_url(scoped_id, file_id)

        archive_contents: bytes = self.get_zip_file(cdn_server_url)

        self.store_mod_archive(archive_contents, mod_name, mod_version)

        return Mod(mod_name, mod_version)
