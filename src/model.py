"""The Model module for Minimal Mod Manager (M3)."""

import csv
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
    DB_DIR,
    DB_GAME_INSTALL_PATH,
    DB_MODS_CSV_PATH,
    DOWNLOADS_DIR,
    GAME_DOMAIN,
    REQUEST_TIMEOUT,
)
from mod import DownloadStatus, InstallStatus, Mod, TreeSet

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
    game_install_path: str
        The absolute path to the game's root folder.
    mods: list of Mod
        List of mod objects to manage as used by controller.

    """

    def __init__(self):
        """Initialize Model class."""
        self.game_install_path: str = self._get_game_install_storage_path()
        self.mods: list[Mod] = []
        self._create_dir(DOWNLOADS_DIR)
        self._create_dir(DB_DIR)
        self._create_mod_list_file()
        self._read_mod_list_file()
        for m in self.mods:
            m.tree = self.get_mod_tree(m)

    def get_mod_tree(self, m: Mod) -> TreeSet:
        """Read mod archive and return a set of file paths."""
        mod_path = Path(DOWNLOADS_DIR) / Path(
            f"{m.name} V{m.version}.zip",
        )
        print("MOD path:", mod_path)
        archive = zipfile.ZipFile(mod_path, "r")
        file_list: list[str] = archive.namelist()
        abs_file_list: list[str] = [
            f"{self.game_install_path}/{f}" for f in file_list
        ]
        return TreeSet({Path(af) for af in abs_file_list})

    def _get_game_install_storage_path(self) -> str:
        if not Path(DB_GAME_INSTALL_PATH).exists():
            return ""
        return Path(DB_GAME_INSTALL_PATH).read_text()

    def _create_dir(self, directory) -> None:
        dir_path = Path(directory)
        if not dir_path.is_dir():
            Path.mkdir(dir_path)

    def _create_mod_list_file(self) -> None:
        if not Path(DB_MODS_CSV_PATH).exists():
            Path(DB_MODS_CSV_PATH).touch()

    def store_game_install_path(self) -> None:
        with Path(DB_GAME_INSTALL_PATH).open("w") as f:
            f.write(self.game_install_path)

    def _read_mod_list_file(self) -> None:
        with Path(DB_MODS_CSV_PATH).open(newline="") as csvfile:
            mod_list = csv.reader(csvfile, delimiter=";")
            for m in mod_list:
                name = m[0]
                version = m[1]
                install_status = InstallStatus(m[2])
                download_status = DownloadStatus(m[3])
                tree: set[Path] = set({Path(p) for p in m[4:]})
                self.mods.append(
                    Mod(name, version, install_status, download_status, tree),
                )

    def write_to_mod_list_file(self) -> None:
        with Path(DB_MODS_CSV_PATH).open(newline="", mode="w") as csvfile:
            csv_writer = csv.writer(csvfile, delimiter=";")
            for m in self.mods:
                if m.tree:
                    csv_writer.writerow(
                        [
                            m.name,
                            m.version,
                            str(m.status["install"].value),
                            str(m.status["download"].value),
                            [str(path) for path in m.tree],
                        ],
                    )
                else:
                    csv_writer.writerow(
                        [
                            m.name,
                            m.version,
                            str(m.status["install"].value),
                            str(m.status["download"].value),
                            str(None),
                        ],
                    )

    def install_mod(self, mod) -> None:
        print("Installing", mod)
        archive_path = Path(DOWNLOADS_DIR + f"{mod.name} V{mod.version}.zip")
        with zipfile.ZipFile(archive_path, "r") as archive:
            archive.extractall(path=self.game_install_path)
            print(
                f"""Extracted contents from '{archive_path}' to \
'{self.game_install_path}'.""",
            )

    def uninstall_mod(self, mod: Mod) -> None:
        print("Uninstalling", mod)
        if mod.tree:
            for entry in mod.tree:
                print("Removing:", entry)
                if entry.is_file():
                    entry.unlink(missing_ok=True)
            for entry in mod.tree:
                if entry.is_dir():
                    # Only removes directory if empty, which is a must
                    # since mods often share some folders!
                    entry.rmdir()
        self._remove_empty_folders()

    def _remove_empty_folders(self) -> None:
        deleted = set()
        for current_dir, subdirs, files in os.walk(
            top=self.game_install_path,
            topdown=False,
        ):
            still_has_subdirs = False
            for subdir in subdirs:
                if os.path.join(current_dir, subdir) not in deleted:  # noqa: PTH118
                    still_has_subdirs = True
                    break

            if not any(files) and not still_has_subdirs:
                os.rmdir(current_dir)  # noqa: PTH106
                deleted.add(current_dir)

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
            path_fragments: list[str] = str(
                object=file_path.with_suffix(suffix=""),
            )[10:].rsplit(
                sep=" V",
                maxsplit=1,
            )
            mod_name, version = path_fragments[0], path_fragments[-1]
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
            Path.cwd() / f"{DOWNLOADS_DIR}/{mod_name} V{mod_version}.zip"
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
