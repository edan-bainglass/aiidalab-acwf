from __future__ import annotations

import traitlets as tl
from IPython.display import Javascript, display

from aiida.engine import submit
from aiida.orm.utils.serialize import serialize
from aiidalab_acwf.common.mixins import HasInputStructure, HasProcess
from aiidalab_acwf.common.wizard import ConfirmableDependentWizardStepModel, State
from aiidalab_acwf.utils import shallow_copy_nested_dict
from aiidalab_acwf.workflows import AcwfAppWorkChain


class SubmissionStepModel(
    ConfirmableDependentWizardStepModel,
    HasInputStructure,
    HasProcess,
):
    identifier = "submission"

    input_parameters = tl.Dict()
    resources = tl.Dict()

    process_label = tl.Unicode("")
    process_description = tl.Unicode("")

    _dependencies = [
        "structure_uuid",
        "input_parameters",
        "resources",
    ]

    def confirm(self):
        super().confirm()
        if not self.has_process:
            self._submit()

    def update(self):
        self.update_process_label()
        self.update_blockers()

    def update_process_label(self):
        if not self.has_structure or not self.input_parameters:
            self.process_label = ""
            return

        structure_label = (
            self.input_structure.label
            if len(self.input_structure.label) > 0
            else self.input_structure.get_formula()
        )

        properties = [p for p in self.input_parameters["properties"] if p != "relax"]
        common_parameters = self.input_parameters.get("common", {})
        relax_type = common_parameters["relax_type"]
        relax_info = "unrelaxed"
        if relax_type != "none":
            relax_info = "relax: atoms+cell" if "cell" in relax_type else "relax: atoms only"
        protocol_info = f"{common_parameters['protocol']} protocol"
        properties_info = f"→ {', '.join(properties)}" if properties else ""

        label_details = [
            relax_info,
            protocol_info,
        ]
        filtered_label_details = [detail for detail in label_details if detail]
        label = f"{structure_label} [{', '.join(filtered_label_details)}] {properties_info}".strip()

        self.process_label = label

    def update_process_metadata(self):
        if not self.has_process:
            return
        self.process_label = self.process.label
        self.process_description = self.process.description
        self.locked = True

    def get_model_state(self) -> dict:
        return {
            "process_label": self.process_label,
            "process_description": self.process_description,
        }

    def set_model_state(self, state: dict):
        self.process_label = state.get("process_label", self.process_label)
        self.process_description = state.get(
            "process_description",
            self.process_description,
        )

    def update_state(self):
        if self.confirmed:
            self.state = State.SUCCESS
        elif self.is_previous_step_successful and (
            self.has_structure and self.input_parameters and self.resources
        ):
            self.state = State.CONFIGURED
        else:
            self.state = State.INIT

    def reset(self):
        with self.hold_trait_notifications():
            self.input_parameters = {}
            self.resources = {}
            self.process_uuid = None

    def _submit(self):
        parameters = shallow_copy_nested_dict(self.input_parameters)
        resources = shallow_copy_nested_dict(self.resources)
        engine = resources.pop("engine", "quantum_espresso")
        builder = AcwfAppWorkChain.get_builder(self.input_structure, parameters, resources, engine)

        with self.hold_trait_notifications():
            process_node = submit(builder)
            process_node.label = self.process_label
            process_node.description = self.process_description
            process_node.base.extras.set("parameters", serialize(parameters))
            process_node.base.extras.set("resources", serialize({"engine": engine, **resources}))
            process_node.base.extras.set("structure", self.input_structure.get_formula())
            self.process_uuid = process_node.uuid
            pk = process_node.pk
            display(Javascript(f"window.history.pushState(null, '', '?pk={pk}');"))

    def _check_blockers(self):
        if not self.has_structure:
            yield "No selected input structure"

        if not self.input_parameters:
            yield "No selected input parameters"

        if not self.resources:
            yield "No selected computational resources"

    def _check_warnings(self):
        """Check for any warnings that should be displayed to the user."""
        return ""
