"""Widgets for computational resource selection."""

from __future__ import annotations

import ipywidgets as ipw

from aiidalab_acwf.common.infobox import InAppGuide
from aiidalab_acwf.common.panel import ResourceSettingsPanel
from aiidalab_acwf.common.widgets import LinkButton
from aiidalab_acwf.common.wizard import ConfirmableDependentWizardStep
from aiidalab_acwf.parameters import DEFAULT_PARAMETERS
from aiidalab_acwf.plugins.utils import get_entry_items

from .common import CommonResourceSettingsModel
from .model import ResourcesStepModel

DEFAULT: dict = DEFAULT_PARAMETERS  # type: ignore


class ResourcesStep(ConfirmableDependentWizardStep[ResourcesStepModel]):
    _missing_message = "Missing input structure and/or workflow configuration"

    def __init__(self, model: ResourcesStepModel, **kwargs):
        super().__init__(
            model=model,
            confirm_kwargs={
                "tooltip": "Confirm the selected resources and go to the next step.",
            },
            **kwargs,
        )

        common_model = CommonResourceSettingsModel(
            default_codes=DEFAULT.get("codes", {}),
            default_user_email=self._model.default_user_email,
        )
        common_panel = ResourceSettingsPanel(model=common_model)

        for _, code_model in common_model.get_models():
            common_panel.register_code_trait_callbacks(code_model)
            code_model.observe(
                self._on_code_selection_change,
                "selected",
            )

        self._model.add_model("common", common_model)

        self.settings = {
            "common": common_panel,
        }

        self._fetch_plugin_resource_settings()

        self._model.observe(
            self._on_input_structure_change,
            "structure_uuid",
        )
        self._model.observe(
            self._on_input_parameters_change,
            "input_parameters",
        )
        self._model.observe(
            self._on_engine_change,
            "engine",
        )

    def reset(self):
        self._model.reset()

    def _render(self):
        super()._render()

        self.engine_selector = ipw.Dropdown()
        ipw.dlink(
            (self._model, "engine_options"),
            (self.engine_selector, "options"),
        )
        ipw.link(
            (self._model, "engine"),
            (self.engine_selector, "value"),
        )

        self.setup_new_codes_button = LinkButton(
            description="Setup resources",
            link="../home/code_setup.ipynb",
            icon="database",
        )

        self.refresh_resources_button = ipw.Button(
            description="Refresh resources",
            icon="refresh",
            tooltip="Refresh the list of available codes",
            button_style="warning",
            layout=ipw.Layout(width="fit-content", margin="2px 2px 12px"),
        )
        self.refresh_resources_button.on_click(self._refresh_resources)

        self.resource_tabs = ipw.Tab(
            layout=ipw.Layout(min_height="250px"),
            selected_index=None,
        )
        self.resource_tabs.observe(
            self._on_resource_tab_change,
            "selected_index",
        )

        self.content.children = [
            InAppGuide(identifier="resources-step"),
            ipw.HBox(
                children=[
                    self.setup_new_codes_button,
                    self.refresh_resources_button,
                ],
                layout=ipw.Layout(grid_gap="5px"),
            ),
            ipw.HBox(
                children=[
                    ipw.HTML("<b>Engine:</b>"),
                    self.engine_selector,
                ],
                layout=ipw.Layout(
                    align_items="center",
                    grid_gap="8px",
                    margin="0 0 8px",
                ),
            ),
            self.resource_tabs,
            self.confirm_box,
        ]

    def _post_render(self):
        super()._post_render()
        self._refresh_resources()
        self._update_resources_panels()

    def _on_input_structure_change(self, _):
        self._model.update()

    def _on_input_parameters_change(self, _):
        self._model.update()
        self._update_resources_panels()

    def _on_engine_change(self, _):
        self._model.update(specific="engine")
        self._update_resources_panels()

    def _on_resource_tab_change(self, change):
        tab_index = change["new"]
        if tab_index is None:
            return
        resources_panel: ResourceSettingsPanel = self.resource_tabs.children[tab_index]
        resources_panel.render()

    def _on_code_selection_change(self, _):
        self._model.update_blockers()

    def _refresh_resources(self, _=None):
        self._model.update()

    def _update_resources_panels(self):
        # TODO simplify - treat SCF as another property, included only if no selected composites
        has_composite_workflow = any(
            identifier != "common" and resources_model.include
            for identifier, resources_model in self._model.get_models()
        )

        children = []
        titles = []
        for identifier, resources_model in self._model.get_models():
            if not resources_model.include:
                continue
            if has_composite_workflow and identifier == "common":
                continue
            resources_panel = self.settings[identifier]
            children.append(resources_panel)
            titles.append(resources_model.title)

        if self.rendered:
            self.resource_tabs.selected_index = None
            self.resource_tabs.children = children
            for index, title in enumerate(titles):
                self.resource_tabs.set_title(index, title)
            self.resource_tabs.selected_index = 0 if children else None
            if children:
                children[0].render()

    def _fetch_plugin_resource_settings(self):
        entries = get_entry_items("aiidalab_acwf", "resources")
        for identifier, resources in entries.items():
            resources_model = resources["model"](
                default_codes=DEFAULT.get("codes", {}),
                default_user_email=self._model.default_user_email,
            )
            resources_panel = ResourceSettingsPanel(model=resources_model)
            for _, code_model in resources_model.get_models():
                resources_panel.register_code_trait_callbacks(code_model)
                code_model.observe(
                    self._on_code_selection_change,
                    "selected",
                )
            self._model.add_model(identifier, resources_model)
            self.settings[identifier] = resources_panel

        self._model.fetched_resources = True
