from .configuration import AfmConfigurationSettingsModel, AfmConfigurationSettingsPanel

afm = {
    "configuration": {
        "model": AfmConfigurationSettingsModel,
        "panel": AfmConfigurationSettingsPanel,
    },
    "resources": {
        "scf": None,
        "ppafm": None,
    },
    "workchain": None,
}
