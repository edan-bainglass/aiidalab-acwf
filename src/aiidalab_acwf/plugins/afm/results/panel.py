from __future__ import annotations

import ipywidgets as ipw

from aiidalab_acwf.common.panel import ResultsPanel

from .model import AfmResultsModel


class AfmResultsPanel(ResultsPanel[AfmResultsModel]):
    def _render(self):
        if not self._model.plot_entries:
            widget = ipw.HTML("<div>No AFM plot images found in outputs.</div>")
            self.results_container.children = [widget]
            return

        images: list[ipw.Image] = []
        for entry in self._model.plot_entries:
            image = ipw.Image(value=entry["payload"], format="png")
            images.append(image)

        widget = ipw.GridBox(images)
        widget.add_class("afm-plots-grid")

        self.results_container.children = [widget]
