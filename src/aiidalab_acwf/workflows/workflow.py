from __future__ import annotations

from aiida_common_workflows.workflows.pp import CommonPostProcessInputGenerator
from aiida_common_workflows.workflows.relax import CommonRelaxInputGenerator

from aiida import orm
from aiida.common import AttributeDict
from aiida.engine import ToContext, WorkChain, if_
from aiida.plugins import DataFactory, WorkflowFactory
from aiidalab_acwf.plugins.utils import get_entry_items
from aiidalab_acwf.utils import shallow_copy_nested_dict

XyData = DataFactory("core.array.xy")
StructureData = DataFactory("core.structure")
BandsData = DataFactory("core.array.bands")
Orbital = DataFactory("core.orbital")

plugin_entries = get_entry_items("aiidalab_acwf", "workchain")


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
        spec.input(
            "engine",
            valid_type=orm.Str,
            default=lambda: orm.Str("quantum_espresso"),
            help="The quantum engine to use for the calculations.",
        )
        spec.expose_inputs(
            CommonRelaxInputGenerator,
            namespace="scf",
            exclude=("structure",),
            namespace_options={
                "required": False,
                "populate_defaults": False,
                "help": "Inputs for the `CommonRelaxWorkChain`, if not specified at all, the relaxation step is skipped.",
            },
        )
        spec.expose_inputs(
            CommonPostProcessInputGenerator,
            namespace="pp",
            exclude=("structure",),
            namespace_options={
                "required": False,
                "populate_defaults": False,
                "help": "Inputs for the `CommonPostProcessWorkChain`, if not specified at all, the post-processing step is skipped.",
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
            cls.run_plugin,
            cls.inspect_plugin,
        )

        spec.exit_code(
            401,
            "ERROR_SUB_PROCESS_FAILED_RELAX",
            message="The CommonRelaxWorkChain sub process failed",
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
        properties = parameters["properties"]
        engine = parameters.pop("engine", "quantum_espresso")
        all_resources = parameters.pop("resources", {})

        for resources in all_resources.values():
            for code in resources["codes"].values():
                if code["code"] is not None:
                    code["code"] = orm.load_code(code["code"])

        # TODO possibly handle pseudos (see comment in QE app workchain)

        builder = cls.get_builder()
        builder.structure = structure
        builder.properties = orm.List(properties)
        builder.engine = orm.Str(engine)

        common_resources = all_resources["common"]

        if "scf" in properties:
            relax_code = common_resources["codes"]["scf"]
            relax_parameters = parameters["common"]
            relax_parameters["engines"] = {
                "relax": {
                    "code": relax_code["code"],
                    "options": {
                        "resources": {
                            "num_machines": relax_code["nodes"],
                            "tot_num_mpiprocs": relax_code["cpus"],
                            "num_cores_per_mpiproc": relax_code["cpus_per_task"],
                            "num_mpiprocs_per_machine": relax_code["ntasks_per_node"],
                        }
                    },
                }
            }
            relax_parameters.update(kwargs)
            builder.relax = relax_parameters
        else:
            builder.pop("relax", None)

        if "pp" in common_resources["codes"]:
            pp_code = common_resources["codes"]["pp"]["code"]
            pp_parameters = {}
            pp_parameters["engines"] = {
                "pp": {
                    "code": pp_code,
                    "options": {
                        "resources": {
                            "num_machines": pp_code["nodes"],
                            "tot_num_mpiprocs": pp_code["cpus"],
                            "num_cores_per_mpiproc": pp_code["cpus_per_task"],
                            "num_mpiprocs_per_machine": pp_code["ntasks_per_node"],
                        }
                    },
                }
            }

        for name, entry_point in plugin_entries.items():
            if name in properties:
                plugin_builder = entry_point["get_builder"](
                    all_resources[name]["codes"],
                    builder.structure,
                    shallow_copy_nested_dict(parameters),
                    **kwargs,
                )
                setattr(builder, name, plugin_builder)
            else:
                builder.pop(name, None)

        return builder

    def setup(self):
        self.ctx.current_structure = self.inputs.structure
        self.ctx.run_relax = "relax" in self.inputs.properties

    def should_run_relax(self):
        """Check if the geometry of the input structure should be optimized."""
        return self.ctx.run_relax

    def run_relax(self):
        inputs = AttributeDict(self.exposed_inputs(CommonRelaxInputGenerator, namespace="relax"))
        inputs.metadata.call_link_label = "relax"
        inputs.structure = self.ctx.current_structure

        engine = self.inputs.engine.value
        RelaxWorkChain = WorkflowFactory(f"common_workflows.relax.{engine}")
        input_generator = RelaxWorkChain.get_input_generator()
        builder = input_generator.get_builder(**inputs)
        running = self.submit(builder)

        self.report(f"launching CommonRelaxWorkChain<{running.pk}>")

        return ToContext(workchain_relax=running)

    def inspect_relax(self):
        """Verify that the `CommonRelaxWorkChain` finished successfully."""
        workchain = self.ctx.workchain_relax

        if not workchain.is_finished_ok:
            self.report(f"CommonRelaxWorkChain failed with exit status {workchain.exit_status}")
            return self.exit_codes.ERROR_SUB_PROCESS_FAILED_RELAX

        if "relaxed_structure" in workchain.outputs:
            self.ctx.current_structure = workchain.outputs.relaxed_structure
            self.out("structure", self.ctx.current_structure)

    def should_run_plugin(self, name):
        return name in self.inputs

    def run_plugin(self):
        """Run the plugin `WorkChain`."""
        plugin_running = {}
        for name, entry_point in plugin_entries.items():
            if not self.should_run_plugin(name):
                continue
            self.report(f"Run workflow: {name}")
            plugin_workchain = entry_point["workchain"]
            inputs = AttributeDict(self.exposed_inputs(plugin_workchain, namespace=name))
            inputs.metadata.call_link_label = name
            if entry_point.get("update_inputs"):
                entry_point["update_inputs"](inputs, self.ctx)
            inputs = prepare_process_inputs(plugin_workchain, inputs)
            running = self.submit(plugin_workchain, **inputs)
            self.report(f"launching plugin {name} <{running.pk}>")
            plugin_running[name] = running

        return ToContext(**plugin_running)

    def inspect_plugin(self):
        """Verify that the `pluginWorkChain` finished successfully."""
        self.report("Inspect plugins:")
        for name, entry_point in plugin_entries.items():
            if not self.should_run_plugin(name):
                continue
            workchain = self.ctx[name]
            if not workchain.is_finished_ok:
                self.report(f"{name} WorkChain failed with exit status {workchain.exit_status}")
                return self.exit_codes.get(f"ERROR_SUB_PROCESS_FAILED_{name}")
            # Attach the output nodes directly as outputs of the workchain.
            self.out_many(self.exposed_outputs(workchain, entry_point["workchain"], namespace=name))

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


def prepare_process_inputs(process, inputs):
    """Prepare the inputs for submission for the given process, according to its spec.

    That is to say that when an input is found in the inputs that corresponds to an input port in the spec of the
    process that expects a `Dict`, yet the value in the inputs is a plain dictionary, the value will be wrapped in by
    the `Dict` class to create a valid input.

    :param process: sub class of `Process` for which to prepare the inputs dictionary
    :param inputs: a dictionary of inputs intended for submission of the process
    :return: a dictionary with all bare dictionaries wrapped in `Dict` if dictated by the process spec
    """
    prepared_inputs = wrap_bare_dict_inputs(process.spec().inputs, inputs)
    return AttributeDict(prepared_inputs)


def wrap_bare_dict_inputs(port_namespace, inputs):
    """Wrap bare dictionaries in `inputs` in a `Dict` node if dictated by the corresponding port in given namespace.

    :param port_namespace: a `PortNamespace`
    :param inputs: a dictionary of inputs intended for submission of the process
    :return: a dictionary with all bare dictionaries wrapped in `Dict` if dictated by the port namespace
    """
    from aiida.engine.processes import PortNamespace

    wrapped = {}

    for key, value in inputs.items():
        if key not in port_namespace:
            wrapped[key] = value
            continue

        port = port_namespace[key]
        valid_types = (
            port.valid_type if isinstance(port.valid_type, (list, tuple)) else (port.valid_type,)
        )

        if isinstance(port, PortNamespace):
            wrapped[key] = wrap_bare_dict_inputs(port, value)
        elif orm.Dict in valid_types and isinstance(value, dict):
            wrapped[key] = orm.Dict(value)
        else:
            wrapped[key] = value

    return wrapped
