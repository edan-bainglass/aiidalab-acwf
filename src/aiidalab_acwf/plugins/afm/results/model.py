from __future__ import annotations

import traitlets as tl

from aiida import orm
from aiidalab_acwf.common.panel import ResultsModel


class AfmResultsModel(ResultsModel):
    title = "AFM"
    identifier = "afm"

    _this_process_label = "AfmWorkChain"

    plot_entries = tl.List(tl.Dict())

    def update(self):
        super().update()
        if not self.has_results:
            self.plot_entries = []
            return

        self.plot_entries = self._collect_plot_entries()

    def _collect_plot_entries(self) -> list[dict]:
        folder = self._get_scan_folder()
        if folder is None:
            return []

        entries = []
        for name in sorted(folder.list_object_names()):
            if name.endswith(".png"):
                payload = self._read_binary(folder, name)
                if payload is not None:
                    entries.append({"name": name, "payload": payload})
                continue

            try:
                nested_names = sorted(folder.list_object_names(name))
            except NotADirectoryError:
                continue

            for nested_name in nested_names:
                if not nested_name.endswith(".png"):
                    continue
                path = f"{name}/{nested_name}"
                payload = self._read_binary(folder, path)
                if payload is not None:
                    entries.append({"name": path, "payload": payload})

        return entries

    def _get_scan_folder(self) -> orm.FolderData | None:
        outputs = self._get_child_outputs()
        for key, value in outputs.items():
            if key.startswith("Q") and isinstance(value, orm.FolderData):
                return value

        namespace = outputs.get("results") if isinstance(outputs, dict) else None
        if namespace is not None:
            for key, value in namespace.items():
                if key.startswith("Q") and isinstance(value, orm.FolderData):
                    return value

        return None

    @staticmethod
    def _read_binary(folder: orm.FolderData, path: str) -> bytes | None:
        try:
            return folder.get_object_content(path, mode="rb")
        except TypeError:
            try:
                text = folder.get_object_content(path)
                return text.encode("latin-1")
            except Exception:
                return None
        except Exception:
            return None
