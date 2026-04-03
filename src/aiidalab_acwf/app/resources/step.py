"""Widgets for computational resource selection."""

from __future__ import annotations

import ipywidgets as ipw

from aiidalab_acwf.common.code import CodeModel
from aiidalab_acwf.common.infobox import InAppGuide
from aiidalab_acwf.common.panel import ResourceSettingsPanel
from aiidalab_acwf.common.widgets import LinkButton
from aiidalab_acwf.common.wizard import ConfirmableDependentWizardStep
from aiidalab_acwf.parameters import DEFAULT_PARAMETERS
from aiidalab_acwf.plugins.utils import get_entry_items

from .model import ResourcesStepModel, WorkflowResourceSettingsModel

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


def _get_ordered_code_names(codes_by_engine: dict[str, object]) -> list[str]:
    ordered: list[str] = []
    seen: set[str] = set()

    for engine_resources in codes_by_engine.values():
        if not isinstance(engine_resources, dict):
            continue
        for code_name in engine_resources:
            key = str(code_name)
            if key in seen:
                continue
            seen.add(key)
            ordered.append(key)

    return ordered


class WorkflowResourceSettingsPanel(ResourceSettingsPanel[WorkflowResourceSettingsModel]):
    def render(self):
        if self.rendered:
            return

        self.code_widgets_container = ipw.VBox()
        self.children = [self.code_widgets_container]

        self.rendered = True

        for _, code_model in self._model.get_models():
            if code_model.is_active:
                self._toggle_code(code_model)

    def _render_code_widget(self, code_model: CodeModel, code_widget):
        super()._render_code_widget(code_model, code_widget)

        def toggle_visibility(_=None, model=code_model):
            widget = self.code_widgets.get(model.name)
            if widget is None:
                return
            widget.layout.display = "block" if model.is_active else "none"

        code_model.observe(toggle_visibility, "is_active")
        toggle_visibility()


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

        self._resource_specs: dict[str, dict[str, dict[str, str]]] = {}
        self._plugin_engine_options: dict[str, list[tuple[str, str]]] = {}
        self.settings: dict[str, WorkflowResourceSettingsPanel] = {}

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

        self.resources_container = ipw.VBox()

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
            self.resources_container,
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

    def _refresh_resources(self, _=None):
        for _, model in self._model.get_models():
            model.refresh_codes()
        self._model.update_blockers()

    def _update_resources_panels(self):
        children = []
        for identifier, model in self._model.get_models():
            if not model.include:
                continue
            panel = self.settings[identifier]
            panel.render()
            children.append(panel)

        if self.rendered:
            self.resources_container.children = children

    def _fetch_plugin_resource_settings(self):
        entries = get_entry_items("aiidalab_acwf", "resources")

        for identifier, resources in entries.items():
            if not isinstance(resources, dict):
                continue

            engine_labels = resources.get("engines", {})
            codes_by_engine = resources.get("codes", {})
            if not isinstance(engine_labels, dict) or not isinstance(codes_by_engine, dict):
                raise TypeError(
                    f"Resources entry '{identifier}' must define 'engines' and 'codes' dictionaries."
                )

            engine_options = [(str(label), str(engine)) for engine, label in engine_labels.items()]
            if not engine_options:
                continue
            self._plugin_engine_options[identifier] = engine_options

            engine_to_resources = {
                engine_name: _get_engine_resources(codes_by_engine, engine_name)
                for _, engine_name in engine_options
            }

            all_code_names = _get_ordered_code_names(codes_by_engine)
            if not all_code_names:
                continue

            model = WorkflowResourceSettingsModel(
                identifier=identifier,
                title=f"{identifier.upper()} resources",
                default_codes=DEFAULT.get("codes", {}),
                default_user_email=self._model.default_user_email,
            )

            current_engine_resources = engine_to_resources.get(
                self._model.selected_engine,
                {},
            )

            for resource_name in all_code_names:
                calc_job_plugin = current_engine_resources.get(resource_name)

                code_model = CodeModel(
                    name=resource_name,
                    description=resource_name,
                    default_calc_job_plugin=calc_job_plugin,
                )
                if calc_job_plugin:
                    code_model.activate()
                else:
                    code_model.deactivate()
                model.add_model(resource_name, code_model)

            panel = WorkflowResourceSettingsPanel(model=model)
            for _, code_model in model.get_models():
                panel.register_code_trait_callbacks(code_model)
                code_model.observe(
                    self._on_code_selection_change,
                    "selected",
                )

            self._model.add_model(identifier, model)
            self.settings[identifier] = panel
            self._resource_specs[identifier] = engine_to_resources

        self._model.fetched_resources = True
        self._update_engine_options()

    def _update_engine_options(self):
        options: list[tuple[str, str]] = []

        properties = [
            prop for prop in self._model.input_parameters.get("properties", []) if prop != "relax"
        ]
        selected_plugin = next(
            (prop for prop in properties if prop in self._plugin_engine_options),
            None,
        )

        if selected_plugin:
            options = self._plugin_engine_options[selected_plugin]
        elif self._plugin_engine_options:
            first_plugin = next(iter(self._plugin_engine_options))
            options = self._plugin_engine_options[first_plugin]

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
        for identifier, resource_specs in self._resource_specs.items():
            model = self._model.get_model(identifier)
            engine_resources = resource_specs.get(engine, {})
            for resource_name, code_model in model.get_models():
                calc_job_plugin = engine_resources.get(resource_name)

                code_model.default_calc_job_plugin = calc_job_plugin
                if calc_job_plugin:
                    code_model.activate()
                else:
                    code_model.deactivate()

                if self.rendered and code_model.is_active and not code_model.is_rendered:
                    panel = self.settings[identifier]
                    panel.render()
                    panel._toggle_code(code_model)

    def _on_code_selection_change(self, _):
        self._model.update_blockers()
