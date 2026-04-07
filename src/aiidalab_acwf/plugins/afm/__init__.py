from pathlib import Path

from .configuration import (
    AfmConfigurationSettingsModel,
    AfmConfigurationSettingsPanel,
    AfmPluginOutline,
)
from .resources import AfmResourceSettingsModel, AfmResourceSettingsPanel
from .results import AfmResultsModel, AfmResultsPanel
from .workflow import workchain_and_builder

afm = {
    "outline": AfmPluginOutline,
    "configuration": {
        "model": AfmConfigurationSettingsModel,
        "panel": AfmConfigurationSettingsPanel,
    },
    "resources": {
        "model": AfmResourceSettingsModel,
        "panel": AfmResourceSettingsPanel,
    },
    "workchain": workchain_and_builder,
    "result": {
        "model": AfmResultsModel,
        "panel": AfmResultsPanel,
    },
    "guides": {
        "title": "Atomic force microscopy (AFM)",
        "path": Path(__file__).resolve().parent / "guides",
    },
}
