import ipywidgets as ipw

import aiidalab_widgets_base as awb

from .model import AppModel


class AcwfApp(ipw.VBox):
    def __init__(self, model: AppModel, **kwargs):
        self._model = model

        header = ipw.HTML(
            value="""
            <h1>AiiDA Common Workflows (ACWF) app</h1>
            <p>
                Submit materials science simulation workflows with your quantum
                engine of choice
            </p>
            """,
        )
        header.add_class("app-header")

        # Workflow selector

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

        # Input section

        self.structure_manager = awb.StructureManagerWidget(
            importers=[],
            editors=[],
            node_class="StructureData",
            storable=False,
            configuration_tabs=[
                "Cell",
                "Selection",
                "Appearance",
                "Download",
            ],
        )
        self.structure_manager.add_class("structure-manager")
        ipw.link(
            (self._model, "structure_uuid"),
            (self.structure_manager, "input_structure"),
            [
                lambda _: self._model.structure,
                lambda structure: structure.uuid if structure else "",
            ],
        )
        ipw.dlink(
            (self._model, "workflow"),
            (self.structure_manager.layout, "display"),
            lambda workflow: "flex" if workflow else "none",
        )

        self.workflow_inputs = ipw.VBox()
        self.workflow_inputs.add_class("workflow-inputs")

        self.confirm_inputs_button = ipw.Button(
            description="Confirm",
            button_style="success",
            icon="check",
        )
        self.confirm_inputs_button.add_class("confirm-inputs-button")
        self.confirm_inputs_button.on_click(
            self._on_workflow_inputs_confirmation,
        )

        self.workflow_configuration = ipw.Accordion(
            children=[
                ipw.VBox(
                    children=[
                        self.workflow_inputs,
                        self.confirm_inputs_button,
                    ],
                    layout=ipw.Layout(grid_gap="12px"),
                ),
            ],
        )
        self.workflow_configuration.set_title(0, "Configure workflow inputs")
        self.workflow_configuration.add_class("workflow-configuration")
        ipw.dlink(
            (self._model, "workflow"),
            (self.workflow_configuration.layout, "display"),
            lambda workflow: "flex" if workflow else "none",
        )
        ipw.dlink(
            (self._model, "workflow"),
            (self.workflow_inputs, "children"),
            lambda workflow: self._get_workflow_input_panel() if workflow else [],
        )

        # Resources section

        self.code_selector = ipw.Dropdown()
        self.code_selector.add_class("code-selector")
        ipw.dlink(
            (self._model, "quantum_engine_options"),
            (self.code_selector, "options"),
        )
        ipw.link(
            (self._model, "quantum_engine"),
            (self.code_selector, "value"),
        )

        self.resource_section = ipw.Accordion(
            children=[
                ipw.VBox(
                    children=[
                        self.code_selector,
                    ]
                )
            ],
            layout=ipw.Layout(display="none"),
        )
        self.resource_section.set_title(0, "Select computational resources")
        self.resource_section.add_class("resource-section")

        # Metadata and submission section

        self.submission = ipw.VBox(
            children=[ipw.HTML("Submission section coming soon!")],
            layout=ipw.Layout(display="none"),
        )
        self.submission.add_class("submission")

        super().__init__(
            children=[
                header,
                workflow_selector_row,
                self.structure_manager,
                self.workflow_configuration,
                self.resource_section,
                self.submission,
            ],
            **kwargs,
        )

    def _on_workflow_inputs_confirmation(self, _):
        self.structure_manager.children[1].selected_index = None
        self.workflow_configuration.selected_index = None
        self.resource_section.layout.display = "flex"

    def _get_workflow_input_panel(self):
        if not self._model.workflow:
            return []

        if self._model.workflow != "afm-scan":
            label = next(
                label
                for label, value in self._model.workflow_options
                if value == self._model.workflow
            )
            return [ipw.HTML(f"{label} not yet supported")]

        return []
