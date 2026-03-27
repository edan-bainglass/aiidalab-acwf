from aiidalab_acwf.common.code.model import CodeModel, PwCodeModel
from aiidalab_acwf.common.panel import (
    PluginResourceSettingsModel,
    PluginResourceSettingsPanel,
)


class BandsResourceSettingsPanel(
    PluginResourceSettingsPanel[BandsResourceSettingsModel],
):
    """Panel for configuring the band structure plugin."""
