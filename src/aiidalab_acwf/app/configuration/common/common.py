from __future__ import annotations

import ipywidgets as ipw

from aiidalab_acwf.common.infobox import InAppGuide
from aiidalab_acwf.common.panel import ConfigurationSettingsPanel
from aiidalab_acwf.common.widgets import HBoxWithUnits

from .model import CommonConfigurationSettingsModel


class CommonConfigurationSettingsPanel(
    ConfigurationSettingsPanel[CommonConfigurationSettingsModel],
):
    def __init__(self, model: CommonConfigurationSettingsModel, **kwargs):
        super().__init__(model, **kwargs)
        self._model.observe(
            self._on_input_structure_change,
            "structure_uuid",
        )

    def render(self):
        if self.rendered:
            return

        self.relax_type = ipw.ToggleButtons()
        ipw.dlink(
            (self._model, "relax_type_options"),
            (self.relax_type, "options"),
        )
        ipw.link(
            (self._model, "relax_type"),
            (self.relax_type, "value"),
        )
        relax_type_label = ipw.Label("Relaxation type:")
        relax_type_label.add_class("settings-label")

        self.electronic_type = ipw.ToggleButtons(style={"description_width": "initial"})
        ipw.dlink(
            (self._model, "electronic_type_options"),
            (self.electronic_type, "options"),
        )
        ipw.link(
            (self._model, "electronic_type"),
            (self.electronic_type, "value"),
        )
        electronic_type_label = ipw.Label("Electronic type:")
        electronic_type_label.add_class("settings-label")

        self.spin_type = ipw.ToggleButtons(style={"description_width": "initial"})
        ipw.dlink(
            (self._model, "spin_type_options"),
            (self.spin_type, "options"),
        )
        ipw.link(
            (self._model, "spin_type"),
            (self.spin_type, "value"),
        )
        spin_type_label = ipw.Label("Spin type:")
        spin_type_label.add_class("settings-label")

        self.protocol = ipw.ToggleButtons()
        ipw.dlink(
            (self._model, "protocol_options"),
            (self.protocol, "options"),
        )
        ipw.link(
            (self._model, "protocol"),
            (self.protocol, "value"),
        )
        protocol_label = ipw.Label("Protocol:")
        protocol_label.add_class("settings-label")

        self.threshold_forces = ipw.BoundedFloatText(
            min=1e-15,
            max=1.0,
            description="Threshold forces:",
            style={"description_width": "118px"},
        )
        ipw.link(
            (self._model, "threshold_forces"),
            (self.threshold_forces, "value"),
        )

        self.threshold_stress = ipw.BoundedFloatText(
            min=1e-15,
            max=1.0,
            description="Threshold stress:",
            style={"description_width": "118px"},
        )
        ipw.link(
            (self._model, "threshold_stress"),
            (self.threshold_stress, "value"),
        )

        self.children = [
            InAppGuide(identifier="common-settings"),
            ipw.HBox(
                children=[
                    relax_type_label,
                    self.relax_type,
                ],
                layout=ipw.Layout(align_items="baseline"),
            ),
            ipw.HBox(
                children=[
                    electronic_type_label,
                    self.electronic_type,
                ],
                layout=ipw.Layout(align_items="baseline"),
            ),
            ipw.HBox(
                children=[
                    spin_type_label,
                    self.spin_type,
                ],
                layout=ipw.Layout(align_items="baseline"),
            ),
            ipw.HBox(
                children=[
                    protocol_label,
                    self.protocol,
                ],
                layout=ipw.Layout(align_items="baseline"),
            ),
            HBoxWithUnits(self.threshold_forces, "eV/Å"),
            HBoxWithUnits(self.threshold_stress, "eV/Å³"),
        ]

        self.rendered = True

    def _on_input_structure_change(self, _):
        self.refresh(specific="structure")
