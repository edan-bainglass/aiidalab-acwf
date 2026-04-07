from __future__ import annotations

import traitlets as tl

from aiidalab_acwf.common.code import CodeModel
from aiidalab_acwf.common.panel import ResourceSettingsModel


class CommonResourceSettingsModel(ResourceSettingsModel):
    title = "Common codes"
    identifier = "common"

    include = tl.Bool(True)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.add_models(
            {
                "scf": CodeModel(
                    name="scf",
                    description="SCF code",
                    default_calc_job_plugin=None,
                ),
            }
        )
