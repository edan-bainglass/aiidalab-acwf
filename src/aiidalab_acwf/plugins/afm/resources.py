from aiidalab_acwf.common.code.model import CodeModel
from aiidalab_acwf.common.panel import PluginResourceSettingsModel, PluginResourceSettingsPanel


class AfmResourceSettingsModel(PluginResourceSettingsModel):
    title = "AFM"
    identifier = "afm"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.add_models(
            {
                "scf": CodeModel(
                    name="scf",
                    description="SCF code",
                    default_calc_job_plugin=None,
                ),
                "pp": CodeModel(
                    name="pp",
                    description="Post-processing code",
                    default_calc_job_plugin=None,
                ),
            }
        )


class AfmResourceSettingsPanel(PluginResourceSettingsPanel[AfmResourceSettingsModel]):
    """Panel for configuring AFM resources."""
