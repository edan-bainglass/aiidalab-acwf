import traitlets as tl

from aiidalab_acwf.common.mixins import HasInputStructure
from aiidalab_acwf.common.panel import PanelModel
from aiidalab_acwf.parameters import DEFAULT_PARAMETERS

DEFAULT: dict = DEFAULT_PARAMETERS  # type: ignore

NO_RELAXATION_OPTION = ("Structure as is", "none")


class CommonConfigurationSettingsModel(
    PanelModel,
    HasInputStructure,
):
    title = "Common settings"
    identifier = "common"

    dependencies = [
        "structure_uuid",
    ]

    relax_type_options = tl.List(default_value=[NO_RELAXATION_OPTION])
    relax_type = tl.Unicode(NO_RELAXATION_OPTION[-1], allow_none=True)

    electronic_type_options = tl.List(
        tl.Tuple(tl.Unicode(), tl.Unicode()),
        [
            ("Metal", "metal"),
            ("Insulator", "insulator"),
        ],
    )
    electronic_type = tl.Unicode(DEFAULT["common"]["electronic_type"])

    spin_type_options = tl.List(
        tl.Tuple(tl.Unicode(), tl.Unicode()),
        [
            ("Off", "none"),
            ("On", "collinear"),
        ],
    )
    spin_type = tl.Unicode(DEFAULT["common"]["spin_type"])

    threshold_forces = tl.Float(0.0)
    threshold_stress = tl.Float(0.0)

    protocol_options = tl.List(
        tl.Tuple(tl.Unicode(), tl.Unicode()),
        [
            ("Fast", "fast"),
            ("Moderate", "moderate"),
            ("Precise", "precise"),
        ],
    )
    protocol = tl.Unicode(DEFAULT["common"]["protocol"])

    include = True

    def update(self, specific=""):
        if specific == "structure":
            self.update_relaxation_options()

    def update_relaxation_options(self):
        if self.has_pbc:
            relax_type_options = [
                NO_RELAXATION_OPTION,
                ("Atomic positions", "positions"),
                ("Full geometry", "positions_cell"),
            ]
        else:
            relax_type_options = [
                NO_RELAXATION_OPTION,
                ("Atomic positions", "positions"),
            ]

        default = DEFAULT["common"]["relax_type"]
        default_available = [default in [option[1] for option in relax_type_options]]
        relax_type = default if default_available else relax_type_options[-1][-1]

        self._defaults = {
            "relax_type_options": relax_type_options,
            "relax_type": relax_type,
        }

        self.relax_type_options = self._get_default("relax_type_options")
        self.relax_type = self._get_default_relax_type()

    def get_model_state(self) -> dict:
        return {
            "relax_type": self.relax_type,
            "electronic_type": self.electronic_type,
            "spin_type": self.spin_type,
            "protocol": self.protocol,
            "threshold_forces": self.threshold_forces,
            "threshold_stress": self.threshold_stress,
        }

    def set_model_state(self, state: dict):
        self.protocol = state.get("protocol", self.protocol)
        self.spin_type = state.get("spin_type", self.spin_type)
        self.electronic_type = state.get("electronic_type", self.electronic_type)
        self.threshold_forces = state.get("threshold_forces", self.threshold_forces)
        self.threshold_stress = state.get("threshold_stress", self.threshold_stress)

    def reset(self):
        with self.hold_trait_notifications():
            self.relax_type_options = self._get_default("relax_type_options")
            self.relax_type = self._get_default_relax_type()
            self.electronic_type = self._get_default("electronic_type")
            self.spin_type = self._get_default("spin_type")
            self.protocol = self._get_default("protocol")
            self.threshold_forces = self._get_default("threshold_forces")
            self.threshold_stress = self._get_default("threshold_stress")

    def _get_default_relax_type(self):
        options = self._get_default("relax_type_options")
        relax_type = self._get_default("relax_type")
        return (
            relax_type
            if relax_type in [option[1] for option in options]
            else options[-1][-1]
        )
