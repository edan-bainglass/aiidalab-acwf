from __future__ import annotations

import ipywidgets as ipw

from aiidalab_acwf.common.code import CodeModel
from aiidalab_acwf.common.panel import ResourceSettingsPanel

from .model import CommonResourceSettingsModel


class CommonResourceSettingsPanel(ResourceSettingsPanel[CommonResourceSettingsModel]):
    def __init__(self, model, **kwargs):
        super().__init__(model, **kwargs)
        self._model.observe(self._on_pp_note_change, "pp_note")

    def render(self):
        if self.rendered:
            return

        self.pp_note = ipw.HTML()
        ipw.dlink((self._model, "pp_note"), (self.pp_note, "value"))
        self.code_widgets_container = ipw.VBox()

        self.children = [
            self.code_widgets_container,
            self.pp_note,
        ]

        self.rendered = True
        self._on_pp_note_change(None)

        for _, code_model in self._model.get_models():
            if code_model.is_active:
                self._toggle_code(code_model)

    def _render_code_widget(self, code_model: CodeModel, code_widget):
        super()._render_code_widget(code_model, code_widget)

        def toggle_visibility(_=None, model=code_model):
            widget = self.code_widgets.get(model.name)
            if widget is None:
                return
            widget.layout.display = "block" if model.is_active else "none"

        code_model.observe(toggle_visibility, "is_active")
        toggle_visibility()

    def _on_pp_note_change(self, _):
        if not self.rendered:
            return
        self.pp_note.layout.display = "block" if self._model.pp_note else "none"
