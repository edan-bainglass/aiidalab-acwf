class BandsResourceSettingsModel(PluginResourceSettingsModel):
    """Model for the band structure plugin."""

    title = "Band structure"
    identifier = "bands"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.add_models(
            {
                "pw": PwCodeModel(
                    name="pw.x",
                    description="pw.x",
                    default_calc_job_plugin="quantumespresso.pw",
                ),
                "projwfc_bands": CodeModel(
                    name="projwfc.x",
                    description="projwfc.x",
                    default_calc_job_plugin="quantumespresso.projwfc",
                ),
            }
        )
