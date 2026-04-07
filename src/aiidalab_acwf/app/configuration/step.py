"""Widgets for the submission of bands work chains.

Authors: AiiDAlab team
"""

from __future__ import annotations

import ipywidgets as ipw

from aiidalab_acwf.common.infobox import InAppGuide
from aiidalab_acwf.common.panel import ConfigurationSettingsPanel, PanelModel, PluginOutline
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

        self.settings = {
            "common": self.common_settings,
        }

        self.available_properties_list = []

        self._fetch_acwf_workflows()

    def reset(self):
        self._model.reset()
        if self.rendered:
            self.sub_steps.selected_index = None
            self.tabs.selected_index = 0

    def _render(self):
        super()._render()

        self.relax_type_help = ipw.HTML()
        ipw.dlink(
            (self._model, "relax_type_help"),
            (self.relax_type_help, "value"),
        )
        self.relax_type = ipw.ToggleButtons()
        ipw.dlink(
            (self._model, "relax_type_options"),
            (self.relax_type, "options"),
        )
        ipw.link(
            (self._model, "relax_type"),
            (self.relax_type, "value"),
        )

        self.tabs = ipw.Tab(
            layout=ipw.Layout(min_height="250px"),
            selected_index=None,
        )
        self.tabs.observe(
            self._on_tab_change,
            "selected_index",
        )

        self.available_properties = ipw.VBox()
        ipw.dlink(
            (self._model, "available_properties_fetched"),
            (self.available_properties, "children"),
            lambda _: self.available_properties_list,
        )

        self.empty_tabs_message = ipw.HTML(
            value=(
                "<p style='margin: 8px 0 0 0;'>"
                "No composite workflows selected. The common SCF base workflow "
                "will still run with the settings from this step."
                "</p>"
            )
        )

        self.settings_wrapper = ipw.VBox(
            children=[
                InAppGuide(identifier="calculation-settings"),
                self.empty_tabs_message,
                self.tabs,
            ]
        )

        self.sub_steps = ipw.Accordion(
            children=[
                ipw.VBox(
                    children=[
                        InAppGuide(identifier="composite-workflow-selection"),
                        self.available_properties,
                    ]
                ),
                self.settings_wrapper,
            ],
            layout=ipw.Layout(margin="10px 2px"),
            selected_index=None,
        )
        self.sub_steps.set_title(0, "Step 2.1: Select composite workflows")
        self.sub_steps.set_title(1, "Step 2.2: Customize calculation parameters")

        self.content.children = [
            InAppGuide(identifier="configuration-step"),
            ipw.HTML(
                """
                <div style="padding-top: 0px; padding-bottom: 0px">
                    <h4>Structure relaxation</h4>
                </div>
                """
            ),
            self.relax_type_help,
            self.relax_type,
            self.sub_steps,
            self.confirm_box,
        ]

    def _post_render(self):
        super()._post_render()
        self._model.update()
        self._update_tabs()

    def _on_tab_change(self, change):
        if (tab_index := change["new"]) is None:
            return
        tab: ConfigurationSettingsPanel = self.tabs.children[tab_index]  # type: ignore
        tab.render()

    def _on_input_structure_change(self, _):
        self._model.update()
        self._model.update_state()

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
            self.tabs.selected_index = 0 if children else None
            self.empty_tabs_message.layout.display = "none" if children else "block"

    def _fetch_acwf_workflows(self):
        outlines = get_entry_items("aiidalab_acwf", "outline")
        entries = get_entry_items("aiidalab_acwf", "configuration")
        for identifier, configuration in entries.items():
            for key in ("panel", "model"):
                if key not in configuration:
                    raise ValueError(f"Entry {identifier} is missing the '{key}' key")

            model: PanelModel = configuration["model"]()
            self._model.add_model(identifier, model)

            outline = outlines.get(identifier)
            outline_widget = outline() if outline else PluginOutline()
            if not outline:
                outline_widget.include.description = model.title or identifier

            info = ipw.HTML()
            ipw.link(
                (model, "include"),
                (outline_widget.include, "value"),
            )

            panel: ConfigurationSettingsPanel = configuration["panel"](model=model)
            self.settings[identifier] = panel

            def toggle_workflow_settings_panel(
                change,
                identifier=identifier,
                model=model,
                info=info,
            ):
                info.value = (
                    f"Customize {identifier} settings in <b>Step 2.2</b>." if change["new"] else ""
                )
                model.update()
                self._update_tabs()

            model.observe(
                toggle_workflow_settings_panel,
                "include",
            )

            self.available_properties_list.append(ipw.HBox(children=[outline_widget, info]))

        self._model.available_properties_fetched = True
