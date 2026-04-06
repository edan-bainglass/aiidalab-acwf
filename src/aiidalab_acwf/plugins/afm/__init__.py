from aiidalab_acwf.common.panel import PluginResourceSettingsPanel

from .configuration import (
    AfmConfigurationSettingsModel,
    AfmConfigurationSettingsPanel,
    AfmPluginOutline,
)
from .resources import AfmResourceSettingsModel
from .result import AfmResultsModel, AfmResultsPanel
from .workflow import workchain_and_builder

afm = {
    "outline": AfmPluginOutline,
    "configuration": {
        "model": AfmConfigurationSettingsModel,
        "panel": AfmConfigurationSettingsPanel,
    },
    "resources": {
        "model": AfmResourceSettingsModel,
        "panel": PluginResourceSettingsPanel[AfmResourceSettingsModel],
        "engines": {
            "quantum_espresso": "Quantum ESPRESSO",
            "cp2k": "CP2K",
        },
        "common_codes": {
            "quantum_espresso": {
                "scf": "quantumespresso.pw",
                "pp": "quantumespresso.pp",
            },
            "cp2k": {
                "scf": "cp2k",
            },
        },
        "plugin_codes": {
            "quantum_espresso": {},
            "cp2k": {},
        },
        "pp_notes": {
            "cp2k": "Post-processing is handled in the selected CP2K SCF code configuration.",
        },
    },
    "workchain": workchain_and_builder,
    "result": {
        "model": AfmResultsModel,
        "panel": AfmResultsPanel,
    },
}
