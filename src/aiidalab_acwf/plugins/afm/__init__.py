from .configuration import AfmConfigurationSettingsModel, AfmConfigurationSettingsPanel
from .workflow import workchain_and_builder

afm = {
    "configuration": {
        "model": AfmConfigurationSettingsModel,
        "panel": AfmConfigurationSettingsPanel,
    },
    "resources": {
        "engines": {
            "quantum_espresso": "Quantum ESPRESSO",
            "cp2k": "CP2K",
        },
        "codes": {
            "quantum_espresso": {
                "scf": "quantumespresso.pw",
                "pp": "quantumespresso.pp",
            },
            "cp2k": {
                "scf": "cp2k",
            },
        },
    },
    "workchain": workchain_and_builder,
}
