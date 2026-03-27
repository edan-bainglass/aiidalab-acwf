import ipywidgets as ipw

from aiidalab_acwf.common.panel import (
    ConfigurationSettingsPanel,
)

from .model import AfmConfigurationSettingsModel


class AfmConfigurationSettingsPanel(
    ConfigurationSettingsPanel[AfmConfigurationSettingsModel]
):
    def render(self):
        if self.rendered:
            return

        self.tip = ipw.Dropdown(description="Tip:")
        ipw.dlink(
            (self._model, "tip_options"),
            (self.tip, "options"),
        )
        ipw.link(
            (self._model, "tip"),
            (self.tip, "value"),
        )

        self.children = [
            self.tip,
        ]

        self.rendered = True
