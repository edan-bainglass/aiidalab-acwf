"""Widgets for the submission of bands work chains.

Authors: AiiDAlab team
"""

from __future__ import annotations

import ipywidgets as ipw

from aiidalab_acwf.common.infobox import InAppGuide
from aiidalab_acwf.common.panel import ConfigurationSettingsPanel, PanelModel
from aiidalab_acwf.common.wizard import ConfirmableDependentWizardStep
from aiidalab_acwf.plugins.utils import get_entry_items

from .common import CommonConfigurationSettingsModel, CommonConfigurationSettingsPanel
from .model import ConfigurationStepModel


class ConfigurationStep(ConfirmableDependentWizardStep[ConfigurationStepModel]):
    _missing_message = "Missing input structure"

    def __init__(self, model: ConfigurationStepModel, **kwargs):
        super().__init__(
            model=model,
            confirm_kwargs={
                "tooltip": "Confirm the currently selected settings and go to the next step",
            },
            **kwargs,
        )

        common_model = CommonConfigurationSettingsModel()
        self.common_settings = CommonConfigurationSettingsPanel(model=common_model)
        self._model.add_model("common", common_model)

        self._model.observe(
            self._on_input_structure_change,
            "structure_uuid",
        )
        self._model.observe(
            self._on_workflow_change,
            "workflow",
        )

        self.settings = {
            "common": self.common_settings,
        }

        self._fetch_acwf_workflows()

    def reset(self):
        self._model.reset()
        if self.rendered:
            self.tabs.selected_index = 0

    def _render(self):
        super()._render()

        self.workflow_selector = ipw.Dropdown()
        self.workflow_selector.add_class("workflow-selector")
        ipw.dlink(
            (self._model, "workflow_options"),
            (self.workflow_selector, "options"),
        )
        ipw.link(
            (self._model, "workflow"),
            (self.workflow_selector, "value"),
        )

        workflow_selector_row = ipw.HBox(
            children=[
                ipw.HTML(value="<b>Workflow:</b>"),
                self.workflow_selector,
            ],
        )
        workflow_selector_row.add_class("workflow-selector-row")

        self.tabs = ipw.Tab(
            layout=ipw.Layout(min_height="250px"),
            selected_index=None,
        )
        self.tabs.observe(
            self._on_tab_change,
            "selected_index",
        )

        self.content.children = [
            InAppGuide(identifier="configuration-step"),
            workflow_selector_row,
            self.tabs,
            self.confirm_box,
        ]

    def _post_render(self):
        super()._post_render()
        self._update_tabs()

    def _on_tab_change(self, change):
        if (tab_index := change["new"]) is None:
            return
        tab: ConfigurationSettingsPanel = self.tabs.children[tab_index]  # type: ignore
        tab.render()

    def _on_input_structure_change(self, _):
        self._model.update()
        self._model.update_state()

    def _on_workflow_change(self, _):
        for identifier, model in self._model.get_models():
            model.include = (
                identifier in self.settings or identifier == self._model.workflow
            )

    def _update_tabs(self):
        children = []
        titles = []
        for identifier, model in self._model.get_models():
            if model.include:
                settings = self.settings[identifier]
                titles.append(model.title)
                children.append(settings)
        if self.rendered:
            self.tabs.selected_index = None
            self.tabs.children = children
            for i, title in enumerate(titles):
                self.tabs.set_title(i, title)
            self.tabs.selected_index = 0

    def _fetch_acwf_workflows(self):
        entries = get_entry_items("aiidalab_acwf", "configuration")

        workflows = []
        for identifier, configuration in entries.items():
            for key in ("panel", "model"):
                if key not in configuration:
                    raise ValueError(f"Entry {identifier} is missing the '{key}' key")

            model: PanelModel = configuration["model"]()
            self._model.add_model(identifier, model)

            panel: ConfigurationSettingsPanel = configuration["panel"](model=model)
            self.settings[identifier] = panel

            workflows.append((model.title, identifier))

            def toggle_workflow_settings_panel(_, model=model):
                model.update()
                self._update_tabs()

            model.observe(
                toggle_workflow_settings_panel,
                "include",
            )

        self._model.workflow_options = [("Select a workflow", ""), *workflows]
