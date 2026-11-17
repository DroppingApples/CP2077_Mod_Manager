from PyQt6.QtWidgets import QDialog, QFileDialog

from model import Model, SearchResult
from view import M3Window


class M3:
    """The Controller class for Minimial Mod Manager"""

    def __init__(self, model: Model, view: M3Window) -> None:
        self._model: Model = model
        self._view: M3Window = view
        self.search_results: list[SearchResult] = []
        self._set_search_results_view()
        self._connect_signals_and_slots()

    def _connect_signals_and_slots(self):
        self._connect_search_button_to_search_for_mods_handler()
        self._connect_download_button_to_download_mod_handler()
        self._connect_game_folder_button_to_file_dialog()

    def _connect_search_button_to_search_for_mods_handler(self) -> None:
        print("Connecting Search Button to self._search_for_mods")
        self._view.search_button.clicked.connect(self._search_for_mods_handler)

    def _connect_download_button_to_download_mod_handler(self) -> None:
        print("Download Button to self._download_mods")
        self._view.download_button.clicked.connect(self._download_mod_handler)

    def _connect_game_folder_button_to_file_dialog(self) -> None:
        self._view.game_folder_button.clicked.connect(self._set_game_folder)

    def _set_game_folder(self) -> None:
        self._view._create_file_dialog()
        if self._view.file_dialog.exec() == QDialog.DialogCode.Accepted:
            self._model.install_folder = self._view.file_dialog.selectedFiles()[0]
            self._view.log_view.addItem(
                f"Game root folder set to {self._model.install_folder}"
            )

    def _read_search_line(self) -> str | None:
        print("Reading Search line...")
        query: str = self._view.search_line.text()
        print("query is", query)
        if query:
            self._view.search_line.setText("")
            return query
        return None

    def _clear_search_results_view(self) -> None:
        print("Clearing Search view")
        self._view.search_results_view.clear()

    def _set_search_results_view(self) -> None:
        self._clear_search_results_view()
        if self.search_results:
            for result in self.search_results:
                print("Adding mod name", result["name"], " to search results view")
                self._view.search_results_view.addItem(result["name"])

    def _search_for_mods_handler(self) -> None:
        print("Searching for mods...")
        query: str | None = self._read_search_line()
        if not query:
            print("No query provided, search aborted")
            return
        print("Searching for mods with query", query)
        self.search_results: list[SearchResult] = self._model.search_mods(query)

        if not self.search_results:
            print("No search results, aborting")
            return
        print("Found following search results:", self.search_results)
        self._set_search_results_view()

    def _download_mod_handler(self) -> None:
        # Assumes that currently selected item in view's search result view
        # is the same index as list[Searchresults] acquired in self._search_for_mods_handler
        current_item = self._view.search_results_view.currentItem()
        if not current_item:
            return
        selected_mod_name: str = current_item.text()
        selected_search_result: SearchResult = next(
            res for res in self.search_results if res["name"] == selected_mod_name
        )
        try:
            self._model.get_mod_file(selected_search_result)
            self._view.mod_list_view.addItem(selected_search_result["name"])
        except FileExistsError:
            self._view.log_view.addItem("Download failed, mod already downloaded.")
