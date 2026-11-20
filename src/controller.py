"""The Controller class for Minimal Mod Manager (M3)."""

from PyQt6.QtWidgets import QDialog, QTableWidgetItem

from mod import Mod
from model import Model, SearchResult
from view import M3Window


class M3:
    """The Controller class for Minimial Mod Manager."""

    def __init__(self, model: Model, view: M3Window) -> None:
        """Initialize the M3 class."""
        self._model: Model = model
        self._view: M3Window = view
        self.search_results: list[SearchResult] = []
        self._set_search_results_view()
        self._connect_signals_and_slots()
        for mod in self._model.mods:
            self.add_mod_to_table(mod)

    def add_mod_to_table(self, mod: Mod) -> None:
        old_row_count = self._view.mod_table.rowCount()
        self._view.mod_table.setRowCount(old_row_count + 1)
        num_rows = self._view.mod_table.rowCount()
        self._view.mod_table.setItem(
            num_rows - 1,
            0,
            QTableWidgetItem(mod.name),
        )
        self._view.mod_table.setItem(
            num_rows - 1,
            1,
            QTableWidgetItem(mod.version),
        )
        self._view.mod_table.setItem(
            num_rows - 1,
            2,
            QTableWidgetItem(mod.status.value),
        )
        self._view.mod_table.resizeColumnsToContents()

    def print_log(self, msg: str) -> None:
        self._view.log_view.addItem(msg)

    def _connect_signals_and_slots(self):
        self._connect_search_button_to_search_for_mods_handler()
        self._connect_download_button_to_download_mod_handler()
        self._connect_game_folder_button_to_file_dialog()

    def _connect_search_button_to_search_for_mods_handler(self) -> None:
        self._view.search_button.clicked.connect(
            self._search_for_mods_handler
        )

    def _connect_download_button_to_download_mod_handler(self) -> None:
        self._view.download_button.clicked.connect(
            self._download_mod_handler
        )

    def _connect_game_folder_button_to_file_dialog(self) -> None:
        self._view.game_folder_button.clicked.connect(
            self._set_game_folder,
        )

    def _set_game_folder(self) -> None:
        self._view.create_file_dialog()
        if self._view.file_dialog.exec() == QDialog.DialogCode.Accepted:
            self._model.install_folder = (
                self._view.file_dialog.selectedFiles()[0]
            )
            self._view.log_view.addItem(
                f"Game root folder set to {self._model.install_folder}",
            )

    def _read_search_line(self) -> str | None:
        query: str = self._view.search_line.text()
        if query:
            self._view.search_line.setText("")
            return query
        return None

    def _clear_search_results_view(self) -> None:
        self._view.search_results_view.clear()

    def _set_search_results_view(self) -> None:
        self._clear_search_results_view()
        if self.search_results:
            for result in self.search_results:
                if result["name"] not in [
                    mod.name for mod in self._model.mods
                ]:
                    self._view.search_results_view.addItem(
                        result["name"]
                    )

    def _search_for_mods_handler(self) -> None:
        print("Searching for mods...")
        query: str | None = self._read_search_line()
        if not query:
            self.print_log(
                "No query provided, search aborted",
            )
            return
        self.print_log(
            f"Searching for mods with query {query}...",
        )

        self.search_results = self._model.search_mods(query)

        if not self.search_results:
            print("No search results, aborting")
            return
        print("Found following search results:", self.search_results)
        self._set_search_results_view()

    def _download_mod_handler(self) -> None:
        # Assumes currently selected item in view's search result view
        # is the same index as list[Searchresults] acquired in
        # self._search_for_mods_handler
        current_item = self._view.search_results_view.currentItem()
        if not current_item:
            return
        selected_mod_name: str = current_item.text()
        selected_search_result: SearchResult = next(
            res
            for res in self.search_results
            if res["name"] == selected_mod_name
        )

        try:
            # TODO: Store mod in db
            mod: Mod = self._model.download_mod(selected_search_result)
            self._model.mods.append(mod)
            self.add_mod_to_table(mod)

        except FileExistsError:
            self.print_log(
                "Download failed, mod already downloaded!",
            )
