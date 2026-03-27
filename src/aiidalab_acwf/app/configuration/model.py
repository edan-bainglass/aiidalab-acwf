from __future__ import annotations

import traitlets as tl
from aiida_common_workflows.common.types import RelaxType

from aiidalab_acwf.common.mixins import (
    HasInputStructure,
    HasModels,
)
from aiidalab_acwf.common.panel import PanelModel
from aiidalab_acwf.common.wizard import ConfirmableDependentWizardStepModel, State
from aiidalab_acwf.parameters import DEFAULT_PARAMETERS

DEFAULT: dict = DEFAULT_PARAMETERS  # type: ignore


class ConfigurationStepModel(
    ConfirmableDependentWizardStepModel,
    HasModels[PanelModel],
    HasInputStructure,
):
    identifier = "configuration"

    workflow_options = tl.List(trait=tl.Tuple(tl.Unicode(), tl.Unicode()))
    workflow = tl.Unicode()

    installed_properties_fetched = tl.Bool(False)

    _dependencies = [
        "structure_uuid",
    ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._default_models = {
            "common",
        }

    def update(self):
        self.update_blockers()

    def get_model_state(self) -> dict:
        state = {
            identifier: model.get_model_state()
            for identifier, model in self.get_models()
            if model.include
        }
        state["properties"] = self._get_properties()
        return state

    def set_model_state(self, state: dict):
        properties = set(state.get("properties", []))
        for identifier, model in self.get_models():
            model.include = identifier in self._default_models | properties
            if state.get(identifier):
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
            for identifier, model in self.get_models():
                if identifier not in self._default_models:
                    model.include = False

    def _link_model(self, model: PanelModel):
        tl.link(
            (self, "confirmed"),
            (model, "confirmed"),
        )
        super()._link_model(model)

    def _get_properties(self):
        properties = []
        for identifier, model in self.get_models():
            if identifier in self._default_models:
                continue
            if model.include:
                properties.append(identifier)
        relax_type = self.get_model("common").relax_type
        if RelaxType(relax_type) is not RelaxType.NONE or not properties:
            properties.append("relax")
        return properties

    def _check_blockers(self):
        if not self.has_structure:
            yield "No selected input structure"

        for _, model in self.get_models():
            if model.is_blocked:
                yield from model.blockers
