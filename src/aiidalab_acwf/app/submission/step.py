"""Widgets for workflow metadata and submission."""

from __future__ import annotations

import ipywidgets as ipw

from aiidalab_acwf.common.infobox import InAppGuide
from aiidalab_acwf.common.wizard import ConfirmableDependentWizardStep

from .model import SubmissionStepModel


class SubmissionStep(ConfirmableDependentWizardStep[SubmissionStepModel]):
    _missing_message = "Missing input structure, workflow configuration, and/or resources"

    def __init__(self, model: SubmissionStepModel, **kwargs):
        super().__init__(
            model=model,
            confirm_kwargs={
                "description": "Submit",
                "tooltip": "Submit the calculation with the selected parameters.",
                "icon": "play",
            },
            **kwargs,
        )

        self._model.observe(
            self._on_input_structure_change,
            "structure_uuid",
        )
        self._model.observe(
            self._on_input_parameters_change,
            "input_parameters",
        )
        self._model.observe(
            self._on_resources_change,
            "resources",
        )
        self._model.observe(
            self._on_process_change,
            "process_uuid",
        )

    def reset(self):
        self._model.reset()

    def _render(self):
        super()._render()

        self.process_label = ipw.Text(
            description="Label",
            layout=ipw.Layout(width="auto"),
        )
        ipw.link(
            (self._model, "process_label"),
            (self.process_label, "value"),
        )
        self.process_description = ipw.Textarea(
            description="Description",
            layout=ipw.Layout(width="auto"),
        )
        ipw.link(
            (self._model, "process_description"),
            (self.process_description, "value"),
        )

        self.warning_messages = ipw.HTML()
        ipw.dlink(
            (self._model, "warning_messages"),
            (self.warning_messages, "value"),
        )

        self.content.children = [
            InAppGuide(identifier="submission-step"),
            self.process_label,
            self.process_description,
            self.warning_messages,
            self.confirm_box,
        ]

    def _on_input_structure_change(self, _):
        self._model.update()
        self._model.update_state()

    def _on_input_parameters_change(self, _):
        self._model.update()
        self._model.update_state()

    def _on_resources_change(self, _):
        self._model.update()
        self._model.update_state()

    def _on_process_change(self, _):
        self._model.update_process_metadata()
