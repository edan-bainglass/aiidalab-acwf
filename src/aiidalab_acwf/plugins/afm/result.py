from __future__ import annotations

import ipywidgets as ipw
import traitlets as tl

from aiida import orm
from aiida.orm.utils.serialize import deserialize_unsafe
from aiidalab_acwf.common.panel import ResultsModel, ResultsPanel


class AfmResultsModel(ResultsModel):
    title = "AFM"
    identifier = "afm"

    _this_process_label = "AfmWorkChain"

    metadata = tl.Dict()
    plot_entries = tl.List(tl.Dict())

    def update(self):
        super().update()
        if not self.has_results:
            self.metadata = {}
            self.plot_entries = []
            return

        self.metadata = self._collect_metadata()
        self.plot_entries = self._collect_plot_entries()

    def _collect_metadata(self) -> dict:
        parameters = self._deserialize_extra("parameters")
        resources = self._deserialize_extra("resources")
        afm_parameters = parameters.get("afm", {})

        outputs = self._get_child_outputs()
        scan_labels = sorted(
            key
            for key, value in outputs.items()
            if key.startswith("Q") and isinstance(value, orm.FolderData)
        )

        return {
            "engine": resources.get("engine", "unknown"),
            "mode": afm_parameters.get("mode", "empirical"),
            "tip": afm_parameters.get("tip", "s"),
            "charge": afm_parameters.get("charge", 0.0),
            "klat": afm_parameters.get("klat", 0.35),
            "scan_min": self._join_vector(afm_parameters.get("scan_min")),
            "scan_max": self._join_vector(afm_parameters.get("scan_max")),
            "scan_step": self._join_vector(afm_parameters.get("scan_step")),
            "scan_outputs": ", ".join(scan_labels) if scan_labels else "none",
        }

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

    def _deserialize_extra(self, key: str) -> dict:
        if not self.process:
            return {}
        value = self.process.base.extras.get(key, {})
        if isinstance(value, str):
            value = deserialize_unsafe(value)
        return value if isinstance(value, dict) else {}

    @staticmethod
    def _join_vector(value):
        if not isinstance(value, (list, tuple)):
            return "n/a"
        return " ".join(str(item) for item in value)

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


class AfmResultsPanel(ResultsPanel[AfmResultsModel]):
    def _render(self):
        metadata_html = self._build_metadata_html()
        plots_widget = self._build_plots_widget()

        self.results_container.children = [
            ipw.HTML("<h3 style='margin: 0 0 8px 0;'>AFM outputs</h3>"),
            metadata_html,
            plots_widget,
        ]

    def _build_metadata_html(self) -> ipw.HTML:
        metadata = self._model.metadata
        rows = []
        for key, value in metadata.items():
            title = key.replace("_", " ").capitalize()
            rows.append(
                f"<tr><td style='padding:4px 8px;'><b>{title}</b></td><td>{value}</td></tr>"
            )

        if not rows:
            rows = ["<tr><td>No metadata available.</td></tr>"]

        return ipw.HTML(
            value=(
                "<table style='width:100%; border-collapse:collapse; margin-bottom:12px;'>"
                f"{''.join(rows)}"
                "</table>"
            )
        )

    def _build_plots_widget(self) -> ipw.Widget:
        if not self._model.plot_entries:
            return ipw.HTML("<div>No AFM plot images found in outputs.</div>")

        cards: list[ipw.Widget] = []
        for entry in self._model.plot_entries:
            image = ipw.Image(
                value=entry["payload"],
                format="png",
                layout=ipw.Layout(width="100%", height="auto"),
            )
            label = ipw.HTML(
                value=f"<div style='font-size:12px; word-break:break-all;'>{entry['name']}</div>"
            )
            cards.append(
                ipw.VBox(
                    children=[image, label],
                    layout=ipw.Layout(
                        border="1px solid #ddd",
                        padding="6px",
                        margin="2px",
                    ),
                )
            )

        return ipw.GridBox(
            children=cards,
            layout=ipw.Layout(
                width="100%",
                grid_template_columns="repeat(auto-fit, minmax(220px, 1fr))",
                grid_gap="8px",
            ),
        )
