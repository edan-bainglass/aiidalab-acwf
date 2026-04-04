"""Widgets for computational resource selection."""

from __future__ import annotations

import ipywidgets as ipw

from aiidalab_acwf.common.infobox import InAppGuide
from aiidalab_acwf.common.panel import ResourceSettingsPanel
from aiidalab_acwf.common.widgets import LinkButton
from aiidalab_acwf.common.wizard import ConfirmableDependentWizardStep
from aiidalab_acwf.parameters import DEFAULT_PARAMETERS
from aiidalab_acwf.plugins.utils import get_entry_items

from .common_settings import CommonResourceSettingsModel, CommonResourceSettingsPanel
from .model import ResourcesStepModel

DEFAULT: dict = DEFAULT_PARAMETERS  # type: ignore


def _get_engine_resources(
    codes_by_engine: dict[str, object],
    engine: str,
) -> dict[str, str]:
    engine_resources = codes_by_engine.get(engine, {})
    if not isinstance(engine_resources, dict):
        return {}
    return {
        str(code_name): calc_job_plugin
        for code_name, calc_job_plugin in engine_resources.items()
        if isinstance(calc_job_plugin, str)
    }


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

        self.settings: dict[str, ResourceSettingsPanel] = {}
        self._plugin_engine_options: dict[str, list[tuple[str, str]]] = {}
        self._plugin_common_resources: dict[str, dict[str, dict[str, str]]] = {}
        self._plugin_resources: dict[str, dict[str, dict[str, str]]] = {}
        self._plugin_pp_notes: dict[str, dict[str, str]] = {}

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
            "selected_engine",
        )

        self._fetch_plugin_resource_settings()

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
            (self._model, "selected_engine"),
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

        self.plugin_tabs = ipw.Tab(layout=ipw.Layout(min_height="250px"), selected_index=None)
        self.plugin_tabs.observe(self._on_plugin_tab_change, "selected_index")

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
                layout=ipw.Layout(align_items="center", grid_gap="8px"),
            ),
            self.plugin_tabs,
            self.confirm_box,
        ]

    def _post_render(self):
        super()._post_render()
        self._update_resources_panels()

    def _on_input_structure_change(self, _):
        self._model.update()

    def _on_input_parameters_change(self, _):
        self._update_engine_options()
        self._model.update()
        self._update_resources_panels()

    def _on_engine_change(self, _):
        self._apply_engine_to_models()
        self._refresh_resources()
        self._update_resources_panels()

    def _on_plugin_tab_change(self, change):
        tab_index = change["new"]
        if tab_index is None:
            return
        panel = self.plugin_tabs.children[tab_index]
        panel.render()  # type: ignore

    def _refresh_resources(self, _=None):
        for _, model in self._model.get_models():
            model.refresh_codes()
        self._model.sync_global_codes()
        self._model.update_blockers()

    def _update_resources_panels(self):
        children = [self.settings["common"]]
        titles = ["Common"]
        for identifier, model in self._model.get_models():
            if identifier == "common" or not model.include:
                continue
            panel = self.settings[identifier]
            children.append(panel)
            titles.append(model.title)

        if self.rendered:
            self.plugin_tabs.selected_index = None
            self.plugin_tabs.children = children
            for index, title in enumerate(titles):
                self.plugin_tabs.set_title(index, title)
            self.plugin_tabs.selected_index = 0
            children[0].render()

    def _fetch_plugin_resource_settings(self):
        common_model = CommonResourceSettingsModel(
            default_codes=DEFAULT.get("codes", {}),
            default_user_email=self._model.default_user_email,
        )
        common_panel = CommonResourceSettingsPanel(model=common_model)
        for _, code_model in common_model.get_models():
            common_panel.register_code_trait_callbacks(code_model)
            code_model.observe(self._on_code_selection_change, "selected")

        self._model.add_model("common", common_model)
        self.settings["common"] = common_panel

        entries = get_entry_items("aiidalab_acwf", "resources")

        for identifier, resources in entries.items():
            if not isinstance(resources, dict):
                continue
            for key in ("model", "panel", "engines"):
                if key not in resources:
                    raise ValueError(f"Resources entry '{identifier}' is missing '{key}'")

            engine_labels = resources["engines"]
            if not isinstance(engine_labels, dict):
                raise TypeError(f"Resources entry '{identifier}' has invalid 'engines' field")

            engine_options = [(str(label), str(engine)) for engine, label in engine_labels.items()]
            if not engine_options:
                continue
            self._plugin_engine_options[identifier] = engine_options

            common_codes_by_engine = resources.get("common_codes", resources.get("codes", {}))
            plugin_codes_by_engine = resources.get("plugin_codes", {})
            if not isinstance(common_codes_by_engine, dict) or not isinstance(
                plugin_codes_by_engine, dict
            ):
                raise TypeError(
                    f"Resources entry '{identifier}' must define mapping fields for codes"
                )

            self._plugin_common_resources[identifier] = {
                engine_name: _get_engine_resources(common_codes_by_engine, engine_name)
                for _, engine_name in engine_options
            }
            self._plugin_resources[identifier] = {
                engine_name: {
                    **_get_engine_resources(common_codes_by_engine, engine_name),
                    **_get_engine_resources(plugin_codes_by_engine, engine_name),
                }
                for _, engine_name in engine_options
            }

            pp_notes = resources.get("pp_notes", {})
            self._plugin_pp_notes[identifier] = (
                {str(engine): str(message) for engine, message in pp_notes.items()}
                if isinstance(pp_notes, dict)
                else {}
            )

            model_cls = resources["model"]
            panel_cls = resources["panel"]
            model = model_cls(
                default_codes=DEFAULT.get("codes", {}),
                default_user_email=self._model.default_user_email,
            )
            panel = panel_cls(model=model)

            for _, code_model in model.get_models():
                panel.register_code_trait_callbacks(code_model)
                code_model.observe(self._on_code_selection_change, "selected")

            self._model.add_model(identifier, model)
            self.settings[identifier] = panel

        self._model.fetched_resources = True
        self._update_engine_options()

    def _update_engine_options(self):
        options: list[tuple[str, str]] = []
        seen_engines = set()

        active_plugins = [
            prop
            for prop in self._model.input_parameters.get("properties", [])
            if prop != "relax" and prop in self._plugin_engine_options
        ]
        source_plugins = active_plugins or list(self._plugin_engine_options.keys())

        for identifier in source_plugins:
            for label, engine in self._plugin_engine_options.get(identifier, []):
                if engine in seen_engines:
                    continue
                seen_engines.add(engine)
                options.append((label, engine))

        valid_engines = {engine for _, engine in options}
        selected_engine = self._model.selected_engine
        if selected_engine not in valid_engines:
            selected_engine = options[0][1] if options else ""

        with self._model.hold_trait_notifications():
            self._model.engine_options = options
            self._model.selected_engine = selected_engine

        self._apply_engine_to_models()

    def _apply_engine_to_models(self):
        engine = self._model.selected_engine
        common_resources = self._resolve_common_resources(engine)
        pp_note = self._resolve_pp_note(engine, common_resources)

        common_model = self._model.get_model("common")
        common_model.set_engine_resources(common_resources, pp_note)

        for identifier, resource_specs in self._plugin_resources.items():
            model = self._model.get_model(identifier)
            model.set_engine_resources(resource_specs.get(engine, {}))

            if not self.rendered:
                continue
            panel = self.settings[identifier]
            for _, code_model in model.get_models():
                if code_model.is_active and not code_model.is_rendered:
                    panel.render()
                    panel._toggle_code(code_model)

        if self.rendered:
            common_panel = self.settings["common"]
            common_panel.render()
            for _, code_model in common_model.get_models():
                if code_model.is_active and not code_model.is_rendered:
                    common_panel._toggle_code(code_model)

        self._model.sync_global_codes()

    def _resolve_common_resources(self, engine: str) -> dict[str, str]:
        merged: dict[str, str] = {}
        active_plugins = [
            prop
            for prop in self._model.input_parameters.get("properties", [])
            if prop != "relax" and prop in self._plugin_common_resources
        ]
        source_plugins = active_plugins or list(self._plugin_common_resources.keys())

        for identifier in source_plugins:
            merged.update(self._plugin_common_resources[identifier].get(engine, {}))

        return merged

    def _resolve_pp_note(self, engine: str, common_resources: dict[str, str]) -> str:
        if "pp" in common_resources:
            return ""

        active_plugins = [
            prop
            for prop in self._model.input_parameters.get("properties", [])
            if prop != "relax" and prop in self._plugin_pp_notes
        ]
        source_plugins = active_plugins or list(self._plugin_pp_notes.keys())
        for identifier in source_plugins:
            message = self._plugin_pp_notes.get(identifier, {}).get(engine)
            if message:
                return message

        return "Post-processing is handled in the selected SCF engine configuration."

    def _on_code_selection_change(self, _):
        self._model.sync_global_codes()
        self._model.update_blockers()
