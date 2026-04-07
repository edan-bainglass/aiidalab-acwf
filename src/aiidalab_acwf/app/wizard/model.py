import typing as t

import traitlets as tl

from aiidalab_acwf.common.mixins import HasModels
from aiidalab_acwf.common.mvc import Model
from aiidalab_acwf.common.wizard import WizardStepModel


class WizardModel(Model, HasModels[WizardStepModel]):
    state = tl.Dict(None, allow_none=True)
    selected_index = tl.Int(None, allow_none=True)
    loading = tl.Bool(False)

    def load_from_state(self, state: dict):
        step_index = state.get("step", 0) - 1
        structure_state = state.get("structure_state")
        configuration_state = state.get("configuration_state")
        resources_state = state.get("resources_state")
        submission_state = state.get("submission_state")
        process_uuid = state.get("process_uuid")

        if step_index >= 0:
            self.loading = True
            structure_model = self.get_model("structure")
            structure_model.set_model_state(structure_state)

            if step_index >= 1:
                structure_model.confirm()
                configuration_model = self.get_model("configure")
                configuration_model.set_model_state(configuration_state)

                if step_index >= 2:
                    configuration_model.confirm()
                    resources_model = self.get_model("resources")
                    resources_model.set_model_state(resources_state)

                    if step_index >= 3:
                        resources_model.confirm()
                        submission_model = self.get_model("submit")
                        submission_model.set_model_state(submission_state or {})

                        if step_index >= 4:
                            submission_model.process_uuid = process_uuid
                            submission_model.confirm()
                            structure_model.lock()
                            configuration_model.lock()
                            resources_model.lock()
                            submission_model.lock()

            self.loading = False

            self.selected_index = step_index

    def update_configuration_model(self):
        structure_model = self.get_model("structure")
        configuration_model = self.get_model("configure")
        if structure_model.confirmed:
            configuration_model.structure_uuid = structure_model.structure_uuid
        else:
            configuration_model.structure_uuid = None

    def update_resources_model(self):
        structure_model = self.get_model("structure")
        configuration_model = self.get_model("configure")
        resources_model = self.get_model("resources")
        if configuration_model.confirmed:
            resources_model.structure_uuid = structure_model.structure_uuid
            resources_model.input_parameters = configuration_model.get_model_state()
        else:
            resources_model.structure_uuid = None
            resources_model.input_parameters = {}

    def update_submission_model(self):
        structure_model = self.get_model("structure")
        configuration_model = self.get_model("configure")
        resources_model = self.get_model("resources")
        submission_model = self.get_model("submit")
        if resources_model.confirmed:
            submission_model.structure_uuid = structure_model.structure_uuid
            submission_model.input_parameters = configuration_model.get_model_state()
            submission_model.resources = resources_model.get_model_state()
            submission_model.update_state()
        else:
            submission_model.structure_uuid = None
            submission_model.input_parameters = {}
            submission_model.resources = {}
            submission_model.update_state()

    def update_results_model(self):
        submission_model = self.get_model("submit")
        results_model = self.get_model("results")
        tl.dlink(
            (submission_model, "process_uuid"),
            (results_model, "process_uuid"),
        )

    def lock_app(self):
        for identifier in ("structure", "configure", "resources", "submit"):
            model = self.get_model(identifier)
            model.lock()

    def auto_advance(self):
        if self.selected_index is None:
            return

        model_list = list(self._models.values())
        index = t.cast(int, self.selected_index)

        if (
            (selected_step := model_list[index]).auto_advance
            and not (index + 1 == len(model_list))
            and selected_step.is_successful
        ):
            self.selected_index += 1
