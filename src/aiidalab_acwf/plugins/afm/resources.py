from __future__ import annotations

from aiidalab_acwf.common.code.model import CodeModel
from aiidalab_acwf.common.panel import ResourceSettingsModel


class AfmResourceSettingsModel(ResourceSettingsModel):
    title = "AFM"
    identifier = "afm"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.add_models(
            {
                "scf": CodeModel(
                    name="scf",
                    description="SCF code",
                ),
                "pp": CodeModel(
                    name="pp",
                    description="Post-processing code",
                ),
            }
        )

    def update(self, specific=""):
        afm_parameters = self.input_parameters.get("afm", {})
        common_parameters = self.input_parameters.get("common", {})

        mode = afm_parameters.get("mode", "empirical")
        relax_type = common_parameters.get("relax_type", "none")

        requires_scf = mode == "hartree" or relax_type != "none"
        requires_pp = mode == "hartree"

        scf_model = self.get_model("scf")
        pp_model = self.get_model("pp")

        supports_scf = bool(scf_model.default_calc_job_plugin)
        supports_pp = bool(pp_model.default_calc_job_plugin)

        scf_model.is_active = supports_scf and requires_scf
        pp_model.is_active = supports_pp and requires_pp
