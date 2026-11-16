from model import Model, SearchResult
from view import M3Window


class M3:
    """The Controller class for Minimial Mod Manager"""

    def __init__(self, model: Model, view: M3Window) -> None:
        self._model: Model = model
        self._view: M3Window = view
        self._connect_signals_and_slots()

    def _connect_signals_and_slots(self):
        self._connect_search_button_to_search_for_mods()

    def _connect_search_button_to_search_for_mods(self) -> None:
        print("Connecting Search Button to self._search_for_mods")
        self._view.search_button.clicked.connect(self._search_for_mods)

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

    def _set_search_results_view(self, search_results: list[SearchResult]) -> None:
        print("Clearing search_results_view")
        self._clear_search_results_view()
        for result in search_results:
            print("Adding mod name", result["name"], " to search results view")
            self._view.search_results_view.addItem(result["name"])

    def _search_for_mods(self) -> None:
        print("Searching for mods...")
        query: str | None = self._read_search_line()
        if not query:
            print("No query provided, search aborted")
            return
        print("Searching for mods with query", query)
        search_results: list[SearchResult] = self._model.search_mods(query)
        print("Found following search results:", search_results)
        self._set_search_results_view(search_results)
