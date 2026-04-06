from __future__ import annotations

import ipywidgets as ipw

from aiidalab_acwf.app.result.components import ResultsComponent
from aiidalab_widgets_base import ProcessNodesTreeWidget
from aiidalab_widgets_base.viewers import AiidaNodeViewWidget

from .model import WorkChainStatusModel


class WorkChainStatusPanel(ResultsComponent[WorkChainStatusModel]):
    def _render(self):
        self.process_tree = ProcessNodesTreeWidget()
        ipw.dlink(
            (self._model, "process_uuid"),
            (self.process_tree, "value"),
        )

        self.node_view = AiidaNodeViewWidget()
        ipw.dlink(
            (self.process_tree, "selected_nodes"),
            (self.node_view, "node"),
            transform=lambda nodes: nodes[0] if nodes else None,
        )

        self.children = [
            self.process_tree,
            self.node_view,
        ]

    def _post_render(self):
        self._select_tree_root()

    def _on_monitor_counter_change(self, _):
        if self.rendered:
            self.process_tree.update()
