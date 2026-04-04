from __future__ import annotations

import traitlets as tl

from aiida import orm
from aiidalab_acwf.common.mixins import HasInputStructure, HasModels
from aiidalab_acwf.common.panel import PluginResourceSettingsModel, ResourceSettingsModel
from aiidalab_acwf.common.wizard import ConfirmableDependentWizardStepModel, State


class ResourcesStepModel(
    ConfirmableDependentWizardStepModel,
    HasModels[ResourceSettingsModel],
    HasInputStructure,
):
    identifier = "resources"

    input_parameters = tl.Dict()

    selected_engine = tl.Unicode("", allow_none=True)
    engine_options = tl.List(
        trait=tl.Tuple(tl.Unicode(), tl.Unicode()),
        default_value=[],
    )

    fetched_resources = tl.Bool(False)
    global_codes = tl.Dict(
        key_trait=tl.Unicode(),
        value_trait=tl.Dict(),
        default_value={},
    )

    _dependencies = [
        "structure_uuid",
        "input_parameters",
        "fetched_resources",
    ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.confirmation_exceptions.append("fetched_resources")
        self.default_user_email = orm.User.collection.get_default().email

    def update(self):
        self.update_plugin_inclusion()
        self.sync_global_codes()
        for _, model in self.get_models():
            model.update()
        self.update_blockers()

    def update_plugin_inclusion(self):
        if not self.input_parameters:
            return
        properties = set(self.input_parameters.get("properties", []))
        for identifier, model in self.get_models():
            if identifier == "common":
                model.include = True
                continue
            model.include = identifier in properties

    def sync_global_codes(self):
        if not self.has_model("common"):
            return

        common_model = self.get_model("common")
        global_codes: dict[str, dict] = {}
        for _, code_model in common_model.get_models():
            if not code_model.is_active or not code_model.default_calc_job_plugin:
                continue
            model_key = code_model.default_calc_job_plugin.replace(".", "__")
            global_codes[model_key] = code_model.get_model_state()

        self.global_codes = global_codes

        for identifier, model in self.get_models():
            if identifier == "common":
                continue
            if isinstance(model, PluginResourceSettingsModel):
                model.global_codes = global_codes

    def get_model_state(self) -> dict:
        state = {
            identifier: model.get_model_state()
            for identifier, model in self.get_models()
            if model.include
        }
        return {
            "engine": self.selected_engine,
            **state,
        }

    def set_model_state(self, state: dict):
        if not state:
            return
        self.selected_engine = state.get("engine", self.selected_engine)
        for identifier, model in self.get_models():
            if identifier in state:
                model.include = True
                model.set_model_state(state[identifier])

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
            for identifier, model in self.get_models():
                model.include = identifier == "common"

    def _check_blockers(self):
        if not self.has_structure:
            yield "No selected input structure"

        if not self.input_parameters:
            yield "No selected input parameters"
            return

        if not self.fetched_resources:
            yield "Resource settings are still loading"
            return

        for identifier, model in self.get_models():
            if not model.include:
                continue
            for code_name, code_model in model.get_models():
                if code_model.is_active and code_model.selected is None:
                    yield f"No code selected for '{code_name}' in panel '{identifier}'."
