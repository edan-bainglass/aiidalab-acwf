from __future__ import annotations

import ipywidgets as ipw

from aiidalab_acwf.common.infobox import InAppGuide
from aiidalab_acwf.common.wizard import ConfirmableWizardStep
from aiidalab_widgets_base import (
    BasicCellEditor,
    BasicStructureEditor,
    SmilesWidget,
    StructureBrowserWidget,
    StructureManagerWidget,
    StructureUploadWidget,
)

from .model import StructureStepModel


class StructureStep(ConfirmableWizardStep[StructureStepModel]):
    """Integrated widget for the selection and edition of structure.
    The widget includes a structure manager that allows to select a structure
    from different sources. It also includes the structure editor. Both the
    structure importers and the structure editors can be extended by plugins.
    """

    def __init__(self, model: StructureStepModel, **kwargs):
        super().__init__(
            model=model,
            confirm_kwargs={
                "tooltip": "Confirm the currently selected structure and go to the next step",
            },
            **kwargs,
        )
        self._model.observe(
            self._on_input_structure_change,
            "structure_uuid",
        )

    def confirm(self, _=None):
        self.manager.store_structure()
        super().confirm()

    def reset(self):
        self._model.reset()

    def render(self):
        if self.rendered:
            # Due to NGLView issues, we need to always "refresh" the widget
            # See post render method for more details
            self._post_render()
        return super().render()

    def _render(self):
        super()._render()

        importers = [
            StructureUploadWidget(title="Upload file"),
            StructureBrowserWidget(title="Browse AiiDA database"),
            SmilesWidget(title="From SMILES"),
        ]

        editors = [
            BasicCellEditor(title="Edit cell"),
            BasicStructureEditor(title="Edit structure"),
        ]

        self.manager = StructureManagerWidget(
            importers=importers,
            editors=editors,
            node_class="StructureData",
            storable=False,
            configuration_tabs=[
                "Cell",
                "Selection",
                "Appearance",
                "Download",
            ],
        )

        if self._model.has_structure:  # preloaded
            # NOTE important to do this prior to setting up the links
            # to avoid an override of the structure in the model,
            # which in turn would trigger a reset of the model
            self.manager.input_structure = self._model.input_structure

        ipw.dlink(
            (self.manager, "structure_node"),
            (self._model, "structure_uuid"),
            lambda node: node.uuid if node else None,
        )
        ipw.dlink(
            (self.manager, "structure_node"),
            (self._model, "structure_name"),
            lambda struct: str(struct.get_formula()) if struct else "",
        )
        ipw.link(
            (self._model, "manager_output"),
            (self.manager.output, "value"),
        )

        self.structure_name = ipw.Text(
            placeholder="[No structure selected]",
            description="Selected:",
            disabled=True,
            layout=ipw.Layout(width="auto", flex="1 1 auto"),
        )
        ipw.dlink(
            (self._model, "structure_name"),
            (self.structure_name, "value"),
        )

        self.content.children = [
            InAppGuide(identifier="structure-step"),
            ipw.HTML("""
                <p>
                    Select a structure from one of the following sources, then
                    click <span style="color: #4caf50;">
                        <i class="fa fa-check-circle"></i> <b>Confirm</b>
                    </span> to go to the next step
                </p>
            """),
            self.manager,
            self.structure_name,
        ]

        self.children = [
            self.content,
            self.confirm_box,
        ]

    def _post_render(self):
        # After rendering the widget, nglview needs to be resized
        # to properly display the structure
        self.manager.viewer._viewer._set_size("100%", "300px")

    def _on_input_structure_change(self, _):
        self._model.update_state()
