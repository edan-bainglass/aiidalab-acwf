from __future__ import annotations

import ipywidgets as ipw

from aiidalab_acwf.common.panel import ResultsPanel

from .model import AfmResultsModel


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
