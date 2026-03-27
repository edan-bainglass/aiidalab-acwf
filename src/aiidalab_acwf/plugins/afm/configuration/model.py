import traitlets as tl

from aiidalab_acwf.common.panel import (
    ConfigurationSettingsModel,
)


class AfmConfigurationSettingsModel(ConfigurationSettingsModel):
    """Model for the AFM configuration settings."""

    title = "AFM"
    identifier = "afm"

    tip: tl.Unicode = tl.Unicode("s")
    tip_options = tl.List(
        trait=tl.Unicode(),
        default_value=["s", "pz", "dz2"],
    )
