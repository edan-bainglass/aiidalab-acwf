from __future__ import annotations

import traitlets as tl

from aiidalab_acwf.common.code import CodeModel
from aiidalab_acwf.common.panel import ResourceSettingsModel


class CommonResourceSettingsModel(ResourceSettingsModel):
    include = tl.Bool(True)
    pp_note = tl.Unicode("")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.identifier = "common"
        self.title = "Common codes"
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

    def set_engine_resources(self, engine_resources: dict[str, str], pp_note: str = ""):
        super().set_engine_resources(engine_resources)
        self.pp_note = pp_note if "pp" not in engine_resources else ""
