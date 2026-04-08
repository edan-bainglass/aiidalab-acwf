from __future__ import annotations

import traitlets as tl

from aiida import orm
from aiidalab_acwf.common.mixins import HasInputStructure, HasModels
from aiidalab_acwf.common.panel import ResourceSettingsModel
from aiidalab_acwf.common.wizard import ConfirmableDependentWizardStepModel, State


class ResourcesStepModel(
    ConfirmableDependentWizardStepModel,
    HasModels[ResourceSettingsModel],
    HasInputStructure,
):
    identifier = "resources"

    input_parameters = tl.Dict()

    engine_options = tl.List(
        trait=tl.Tuple(tl.Unicode(), tl.Unicode()),
        default_value=[
            ("Quantum ESPRESSO", "quantum_espresso"),
            ("CP2K", "cp2k"),
        ],
    )
    engine = tl.Unicode("quantum_espresso", allow_none=True)

    fetched_resources = tl.Bool(False)

    _dependencies = [
        "structure_uuid",
        "input_parameters",
        "fetched_resources",
    ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.confirmation_exceptions.append("fetched_resources")
        self.default_user_email = orm.User.collection.get_default().email

    def update(self, specific=""):
        self.update_plugin_inclusion()
        for _, resources_model in self.get_models():
            resources_model.update(specific)
        self.update_blockers()

    def update_plugin_inclusion(self):
        properties = set(self.input_parameters.get("properties", []))
        for identifier, resources_model in self.get_models():
            if identifier == "common":
                resources_model.include = not properties
            else:
                resources_model.include = identifier in properties

    def get_model_state(self) -> dict:
        state = {
            identifier: resources_model.get_model_state()
            for identifier, resources_model in self.get_models()
            if resources_model.include
        }
        return {
            "engine": self.engine,
            **state,
        }

    def set_model_state(self, state: dict):
        if not state:
            return
        self.engine = state.get("engine", self.engine)
        for identifier, resources_model in self.get_models():
            if identifier in state:
                resources_model.include = True
                resources_model.set_model_state(state[identifier])

    def update_state(self):
        if self.confirmed:
            self.state = State.SUCCESS
        elif self.is_previous_step_successful and self.has_all_dependencies:
            self.state = State.CONFIGURED
        else:
            self.state = State.INIT

    def reset(self):
        self.confirmed = False
        with self.hold_trait_notifications():
            self.input_parameters = {}
            self.fetched_resources = False
            for identifier, resources_model in self.get_models():
                resources_model.include = identifier == "common"

    def _check_blockers(self):
        if not self.has_structure:
            yield "No selected input structure"

        if not self.input_parameters:
            yield "No selected input parameters"
            return

        if not self.fetched_resources:
            yield "Resource settings are still loading"
            return

        for identifier, resources_model in self.get_models():
            if not resources_model.include:
                continue
            for code_name, code_model in resources_model.get_models():
                if code_model.is_active and code_model.selected is None:
                    yield f"No code selected for '{code_name}' in panel '{identifier}'."
