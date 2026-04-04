import traitlets as tl

from aiidalab_acwf.common.mixins import HasInputStructure
from aiidalab_acwf.common.panel import PanelModel
from aiidalab_acwf.parameters import DEFAULT_PARAMETERS

DEFAULT: dict = DEFAULT_PARAMETERS  # type: ignore


class CommonConfigurationSettingsModel(
    PanelModel,
    HasInputStructure,
):
    title = "Common settings"
    identifier = "common"

    dependencies = [
        "structure_uuid",
    ]

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
        return

    def get_model_state(self) -> dict:
        return {
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
            self.electronic_type = self._get_default("electronic_type")
            self.spin_type = self._get_default("spin_type")
            self.protocol = self._get_default("protocol")
            self.threshold_forces = self._get_default("threshold_forces")
            self.threshold_stress = self._get_default("threshold_stress")
