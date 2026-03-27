from __future__ import annotations

from aiida_common_workflows.workflows.relax.workchain import CommonRelaxWorkChain

from aiida import orm
from aiida.common import AttributeDict
from aiida.engine import ToContext, WorkChain, if_
from aiida.plugins import DataFactory
from aiidalab_acwf.plugins.utils import get_entry_items

XyData = DataFactory("core.array.xy")
StructureData = DataFactory("core.structure")
BandsData = DataFactory("core.array.bands")
Orbital = DataFactory("core.orbital")

plugin_entries = get_entry_items("acwf", "workchain")


class AcwfAppWorkChain(WorkChain):
    """WorkChain designed to calculate the requested properties in the AiiDAlab Quantum ESPRESSO app."""

    @classmethod
    def define(cls, spec):
        """Define the process specification."""
        super().define(spec)

        spec.input(
            "structure",
            valid_type=StructureData,
            help="The inputs structure.",
        )
        spec.input(
            "properties",
            valid_type=orm.List,
            default=orm.List,
            help="The properties to compute in the workflow.",
        )
        spec.expose_inputs(
            CommonRelaxWorkChain,
            namespace="relax",
            exclude=("structure",),
            namespace_options={
                "required": False,
                "populate_defaults": False,
                "help": "Inputs for the `CommonRelaxWorkChain`, if not specified at all, the relaxation step is skipped.",
            },
        )

        i = 0
        for name, entry_point in plugin_entries.items():
            plugin_workchain = entry_point["workchain"]
            spec.expose_inputs(
                plugin_workchain,
                namespace=name,
                exclude=entry_point.get("exclude"),
                namespace_options={
                    "required": False,
                    "populate_defaults": False,
                    "help": f"Inputs for the {name} plugin.",
                },
            )
            spec.expose_outputs(
                plugin_workchain,
                namespace=name,
                namespace_options={"required": False},
            )
            spec.exit_code(
                403 + i,
                f"ERROR_SUB_PROCESS_FAILED_{name}",
                message=f"The plugin {name} WorkChain sub process failed",
            )
            i += 1

        spec.outline(
            cls.setup,
            if_(cls.should_run_relax)(
                cls.run_relax,
                cls.inspect_relax,
            ),
            cls.run_workflow,
            cls.inspect_workflow,
        )

        spec.exit_code(
            401,
            "ERROR_SUB_PROCESS_FAILED_RELAX",
            message="The PwRelaxWorkChain sub process failed",
        )
        spec.exit_code(
            402,
            "ERROR_SUB_PROCESS_FAILED_PDOS",
            message="The PdosWorkChain sub process failed",
        )

        spec.output("structure", valid_type=StructureData, required=False)

    @classmethod
    def get_builder_from_protocol(
        cls,
        structure,
        parameters=None,
        **kwargs,
    ):
        parameters = parameters or {}
        codes = parameters.pop("codes", {})

        for _, plugin_codes in codes.items():
            for _, value in plugin_codes["codes"].items():
                if value["code"] is not None:
                    value["code"] = orm.load_node(value["code"])

        builder = cls.get_builder()
        builder.structure = structure
        return builder

    def setup(self):
        self.ctx.current_structure = self.inputs.structure
        self.ctx.run_relax = "relax" in self.inputs.properties

    def should_run_relax(self):
        """Check if the geometry of the input structure should be optimized."""
        return self.ctx.run_relax

    def run_relax(self):
        inputs = AttributeDict(
            self.exposed_inputs(CommonRelaxWorkChain, namespace="relax")
        )
        inputs.metadata.call_link_label = "relax"
        inputs.structure = self.ctx.current_structure

        # TODO we should be submitting the code-specific implementation here
        running = self.submit(CommonRelaxWorkChain, **inputs)

        self.report(f"launching CommonRelaxWorkChain<{running.pk}>")

        return ToContext(workchain_relax=running)

    def inspect_relax(self):
        """Verify that the `CommonRelaxWorkChain` finished successfully."""
        workchain = self.ctx.workchain_relax

        if not workchain.is_finished_ok:
            self.report(
                f"PwRelaxWorkChain failed with exit status {workchain.exit_status}"
            )
            return self.exit_codes.ERROR_SUB_PROCESS_FAILED_RELAX

        if "output_structure" in workchain.outputs:
            self.ctx.current_structure = workchain.outputs.output_structure
            self.ctx.current_number_of_bands = (
                workchain.outputs.output_parameters.get_attribute("number_of_bands")
            )
            self.out("structure", self.ctx.current_structure)

    def should_run_plugin(self, name):
        return name in self.inputs

    def run_workflow(self):
        pass

    def inspect_workflow(self):
        pass

    def on_terminated(self):
        """Clean the working directories of all child calculations if `clean_workdir=True` in the inputs."""
        super().on_terminated()

        if self.inputs.clean_workdir.value is False:
            self.report("remote folders will not be cleaned")
            return

        cleaned_calcs = []

        for called_descendant in self.node.called_descendants:
            if isinstance(called_descendant, orm.CalcJobNode):
                try:
                    called_descendant.outputs.remote_folder._clean()  # pylint: disable=protected-access
                    cleaned_calcs.append(called_descendant.pk)
                except (OSError, KeyError):
                    pass

        if cleaned_calcs:
            self.report(
                f"cleaned remote folders of calculations: {' '.join(map(str, cleaned_calcs))}"
            )
