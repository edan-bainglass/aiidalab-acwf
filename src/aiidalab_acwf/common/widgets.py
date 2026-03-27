from __future__ import annotations

import anywidget
import ipywidgets as ipw
import traitlets

from aiida.orm import load_code
from aiidalab_widgets_base import ComputationalResourcesWidget

from .link_button import LinkButton

__all__ = ["LinkButton"]


class QEAppComputationalResourcesWidget(ipw.VBox):
    value = traitlets.Unicode(allow_none=True)
    nodes = traitlets.Int(default_value=1)
    cpus = traitlets.Int(default_value=1)

    def __init__(self, **kwargs):
        """Widget to setup the compute resources, which include the code,
        the number of nodes and the number of cpus.
        """
        self.code_selection = ComputationalResourcesWidget(
            description=kwargs.pop("description", None),
            default_calc_job_plugin=kwargs.pop("default_calc_job_plugin", None),
            include_setup_widget=False,
            fetch_codes=False,
            **kwargs,
        )
        self.code_selection.layout.width = "80%"

        self.num_nodes = ipw.BoundedIntText(
            value=1,
            step=1,
            min=1,
            max=1000,
            description="Nodes",
        )

        self.num_cpus = ipw.BoundedIntText(
            value=1,
            step=1,
            min=1,
            description="CPUs",
        )

        self.btn_setup_resource_detail = ipw.ToggleButton(description="More")
        self.btn_setup_resource_detail.observe(self._setup_resource_detail, "value")
        self._setup_resource_detail_output = ipw.VBox(layout={"width": "500px"})

        # combine code, nodes and cpus
        children = [
            ipw.HBox(
                children=[
                    self.code_selection,
                    self.num_nodes,
                    self.num_cpus,
                    self.btn_setup_resource_detail,
                ]
            ),
            self._setup_resource_detail_output,
        ]
        super().__init__(children=children, **kwargs)

        self.resource_detail = ResourceDetailSettings()
        traitlets.dlink(
            (self.num_cpus, "value"), (self.resource_detail.ntasks_per_node, "value")
        )
        traitlets.link((self.code_selection, "value"), (self, "value"))

    def update_resources(self, change):
        if change["new"]:
            self.set_resource_defaults(load_code(change["new"]).computer)

    def set_resource_defaults(self, computer=None):
        if computer is None:
            self.num_nodes.disabled = True
            self.num_nodes.value = 1
            self.num_cpus.max = 1
            self.num_cpus.value = 1
            self.num_cpus.description = "CPUs"
        else:
            default_mpiprocs = computer.get_default_mpiprocs_per_machine()
            self.num_nodes.disabled = (
                True if computer.hostname == "localhost" else False
            )
            self.num_cpus.max = default_mpiprocs
            self.num_cpus.value = (
                1 if computer.hostname == "localhost" else default_mpiprocs
            )
            self.num_cpus.description = "CPUs"

    @property
    def parameters(self):
        return self.get_parameters()

    def get_parameters(self):
        """Return the parameters."""
        parameters = {
            "code": self.code_selection.value,
            "nodes": self.num_nodes.value,
            "cpus": self.num_cpus.value,
        }
        parameters.update(self.resource_detail.parameters)
        return parameters

    @parameters.setter
    def parameters(self, parameters):
        self.set_parameters(parameters)

    def set_parameters(self, parameters):
        """Set the parameters."""
        self.code_selection.value = parameters["code"]
        if "nodes" in parameters:
            self.num_nodes.value = parameters["nodes"]
        if "cpus" in parameters:
            self.num_cpus.value = parameters["cpus"]
        if "ntasks_per_node" in parameters:
            self.resource_detail.ntasks_per_node.value = parameters["ntasks_per_node"]
        if "cpus_per_task" in parameters:
            self.resource_detail.cpus_per_task.value = parameters["cpus_per_task"]
        if "max_wallclock_seconds" in parameters:
            self.resource_detail.max_wallclock_seconds.value = parameters[
                "max_wallclock_seconds"
            ]

    def _setup_resource_detail(self, _=None):
        if self.btn_setup_resource_detail.value:
            self._setup_resource_detail_output.layout = {
                "width": "500px",
                "border": "1px solid gray",
            }
            self._setup_resource_detail_output.children = [
                self.resource_detail,
            ]
        else:
            self._setup_resource_detail_output.layout = {
                "width": "500px",
                "border": "none",
            }
            self._setup_resource_detail_output.children = []


class ResourceDetailSettings(ipw.VBox):
    """Widget for setting the Resource detail."""

    prompt = ipw.HTML(
        """<div style="line-height:120%; padding-top:0px">
        <p style="padding-bottom:10px">
        Specify the parameters for the scheduler (only for advanced user). <br>
        These should be specified accordingly to the computer where the code will run.
        </p></div>"""
    )

    def __init__(self, **kwargs):
        self.ntasks_per_node = ipw.BoundedIntText(
            value=1,
            step=1,
            min=1,
            max=1000,
            description="ntasks-per-node",
            style={"description_width": "100px"},
        )
        self.cpus_per_task = ipw.BoundedIntText(
            value=1,
            step=1,
            min=1,
            description="cpus-per-task",
            style={"description_width": "100px"},
        )
        self.max_wallclock_seconds = ipw.BoundedIntText(
            value=3600 * 12,
            step=3600,
            min=60 * 10,
            max=3600 * 24,
            description="max seconds",
            style={"description_width": "100px"},
        )
        super().__init__(
            children=[
                self.prompt,
                self.ntasks_per_node,
                self.cpus_per_task,
                self.max_wallclock_seconds,
            ],
            **kwargs,
        )

    @property
    def parameters(self):
        return self.get_parameters()

    def get_parameters(self):
        """Return the parameters."""
        return {
            "ntasks_per_node": self.ntasks_per_node.value,
            "cpus_per_task": self.cpus_per_task.value,
            "max_wallclock_seconds": self.max_wallclock_seconds.value,
        }

    @parameters.setter
    def parameters(self, parameters):
        self.ntasks_per_node.value = parameters.get("ntasks_per_node", 1)
        self.cpus_per_task.value = parameters.get("cpus_per_task", 1)
        self.max_wallclock_seconds.value = parameters.get(
            "max_wallclock_seconds", 3600 * 12
        )

    def reset(self):
        """Reset the settings."""
        self.ntasks_per_node.value = 1
        self.cpus_per_task.value = 1
        self.max_wallclock_seconds.value = 3600 * 12


class ParallelizationSettings(ipw.VBox):
    """Widget for setting the parallelization settings."""

    prompt = ipw.HTML(
        """<div style="line-height:120%; padding-top:0px">
        <p style="padding-bottom:10px">
        Specify the number of k-points pools for the pw.x calculations (only for advanced user).
        </p></div>"""
    )

    def __init__(self, **kwargs):
        extra = {
            "style": {"description_width": "150px"},
            "layout": {"min_width": "180px"},
        }
        self.npool = ipw.BoundedIntText(
            value=1, step=1, min=1, max=128, description="Number of k-pools", **extra
        )
        self.override = ipw.Checkbox(
            description="",
            indent=False,
            value=False,
            layout=ipw.Layout(max_width="20px"),
        )
        self.override.observe(self.set_visibility, "value")
        super().__init__(
            children=[
                ipw.HBox(
                    children=[self.override, self.prompt, self.npool],
                    layout=ipw.Layout(justify_content="flex-start"),
                ),
            ],
            **kwargs,
        )
        # set the default visibility of the widget
        self.npool.layout.display = "none"

    def set_visibility(self, change):
        if change["new"]:
            self.npool.layout.display = "block"
        else:
            self.npool.layout.display = "none"

    def reset(self):
        """Reset the parallelization settings."""
        self.npool.value = 1


class PwCodeResourceSetupWidget(QEAppComputationalResourcesWidget):
    """ComputationalResources Widget for the pw.x calculation."""

    nodes = traitlets.Int(default_value=1)

    def __init__(self, **kwargs):
        # By definition, npool must be a divisor of the total number of k-points
        # thus we can not set a default value here, or from the computer.
        self.parallelization = ParallelizationSettings()
        super().__init__(**kwargs)
        # add nodes and cpus into the children of the widget
        self.children += (self.parallelization,)

    def get_parallelization(self):
        """Return the parallelization settings."""
        parallelization = (
            {"npool": self.parallelization.npool.value}
            if self.parallelization.override.value
            else {}
        )
        return parallelization

    def set_parallelization(self, parallelization):
        """Set the parallelization settings."""
        if "npool" in parallelization:
            self.parallelization.override.value = True
            self.parallelization.npool.value = parallelization["npool"]

    def get_parameters(self):
        """Return the parameters."""
        parameters = super().get_parameters()
        parameters.update({"parallelization": self.get_parallelization()})
        return parameters

    def set_parameters(self, parameters):
        """Set the parameters."""
        super().set_parameters(parameters)
        if "parallelization" in parameters:
            self.set_parallelization(parameters["parallelization"])


class TableWidget(anywidget.AnyWidget):
    _esm = """
    function render({ model, el }) {
        let domElement = document.createElement("div");
        el.classList.add("custom-table");
        let selectedIndices = [];

        function drawTable() {
            const data = model.get("data");
            domElement.innerHTML = "";
            let innerHTML = '<table><tr>' + data[0].map(header => `<th>${header}</th>`).join('') + '</tr>';

            for (let i = 1; i < data.length; i++) {
                innerHTML += '<tr>' + data[i].map(cell => `<td>${cell}</td>`).join('') + '</tr>';
            }

            innerHTML += "</table>";
            domElement.innerHTML = innerHTML;

            const rows = domElement.querySelectorAll('tr');
            rows.forEach((row, index) => {
                if (index > 0) {
                    row.addEventListener('click', () => {
                        const rowIndex = index - 1;
                        if (selectedIndices.includes(rowIndex)) {
                            selectedIndices = selectedIndices.filter(i => i !== rowIndex);
                            row.classList.remove('selected-row');
                        } else {
                            selectedIndices.push(rowIndex);
                            row.classList.add('selected-row');
                        }
                        model.set('selected_rows', [...selectedIndices]);
                        model.save_changes();
                    });

                    row.addEventListener('mouseover', () => {
                        if (!row.classList.contains('selected-row')) {
                            row.classList.add('hover-row');
                        }
                    });

                    row.addEventListener('mouseout', () => {
                        row.classList.remove('hover-row');
                    });
                }
            });
        }

        function updateSelection() {
            const newSelection = model.get("selected_rows");
            selectedIndices = [...newSelection]; // Synchronize the JavaScript state with the Python state
            const rows = domElement.querySelectorAll('tr');
            rows.forEach((row, index) => {
                if (index > 0) {
                    if (selectedIndices.includes(index - 1)) {
                        row.classList.add('selected-row');
                    } else {
                        row.classList.remove('selected-row');
                    }
                }
            });
        }

        drawTable();
        model.on("change:data", drawTable);
        model.on("change:selected_rows", updateSelection);
        el.appendChild(domElement);
    }
    export default { render };
    """
    _css = """
    .custom-table table, .custom-table th, .custom-table td {
        border: 1px solid black;
        border-collapse: collapse;
        text-align: left;
        padding: 4px;
    }
    .custom-table th, .custom-table td {
        min-width: 50px;
        word-wrap: break-word;
    }
    .custom-table table {
        width: 70%;
        font-size: 1.0em;
    }
    /* Hover effect with light gray background */
    .custom-table tr.hover-row:not(.selected-row) {
        background-color: #f0f0f0;
    }
    /* Selected row effect with light green background */
    .custom-table tr.selected-row {
        background-color: #DFF0D8;
    }
    """
    data = traitlets.List().tag(sync=True)
    selected_rows = traitlets.List().tag(sync=True)


class HBoxWithUnits(ipw.HBox):
    def __init__(self, widget: ipw.ValueWidget, units: str, **kwargs):
        super().__init__(
            children=[
                widget,
                ipw.HTML(units),
            ],
            layout={
                "align_items": "center",
                "grid_gap": "2px",
            }
            | kwargs.pop("layout", {}),
            **kwargs,
        )
        self.add_class("hbox-with-units")


class WarningWidget(ipw.HTML):
    message = traitlets.Unicode()

    _TEMPLATE = """
        <div class="alert alert-danger" style="text-align: center; margin-bottom: 0;">
            <b>{message}</b>
        </div>
    """

    def __init__(self, message: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.message = message

    @traitlets.observe("message")
    def _update_message(self, change: dict):
        self.value = self._TEMPLATE.format(message=change["new"])
