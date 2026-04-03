from .configuration import AfmConfigurationSettingsModel, AfmConfigurationSettingsPanel
from .workflow import workchain_and_builder

afm = {
    "configuration": {
        "model": AfmConfigurationSettingsModel,
        "panel": AfmConfigurationSettingsPanel,
    },
    "resources": {
        "scf": None,
        "pp": None,
        "ppafm": None,
    },
    "workchain": workchain_and_builder,
}
