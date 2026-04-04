from __future__ import annotations

from aiida_common_workflows.workflows.afm import AfmCase, AfmWorkflow
from aiida_workgraph.engine.workgraph import WorkGraphEngine

from aiida.engine import ToContext, WorkChain


def _options_from_code_settings(code_settings: dict) -> dict:
    return {
        "resources": {
            "num_machines": code_settings.get("nodes", 1),
            "tot_num_mpiprocs": code_settings.get("cpus", 1),
            "num_cores_per_mpiproc": code_settings.get("cpus_per_task", 1),
            "num_mpiprocs_per_machine": code_settings.get("ntasks_per_node", 1),
        },
        "max_wallclock_seconds": code_settings.get("max_wallclock_seconds", 43200),
    }


def _code_settings(code_settings: dict) -> dict:
    return {
        "code": code_settings.get("code"),
        "options": _options_from_code_settings(code_settings),
    }


def _translate_afm_params(afm_parameters: dict) -> dict:
    return {
        "PBC": afm_parameters.get("pbc", True),
        "tip": afm_parameters.get("tip", "s"),
        "klat": afm_parameters.get("klat", 0.5),
        "krad": afm_parameters.get("krad", 20.0),
        "gridA": list(afm_parameters.get("grid_a", (20.0, 0.0, 0.0))),
        "gridB": list(afm_parameters.get("grid_b", (0.0, 20.0, 0.0))),
        "gridC": list(afm_parameters.get("grid_c", (0.0, 0.0, 20.0))),
        "sigma": afm_parameters.get("sigma", 0.7),
        "charge": afm_parameters.get("charge", 0.0),
        "r0Probe": list(afm_parameters.get("r0_probe", (0.0, 0.0, 4.0))),
        "scanMax": list(afm_parameters.get("scan_max", (0.1, 0.1, 0.1))),
        "scanMin": list(afm_parameters.get("scan_min", (0.0, 0.0, 5.0))),
        "scanStep": list(afm_parameters.get("scan_step", (20.0, 20.0, 8.0))),
        "Amplitude": afm_parameters.get("amplitude", 1.0),
        "probeType": afm_parameters.get("probe_type", "O"),
        "f0Cantilever": afm_parameters.get("f0_cantilever", 30300.0),
        "gridN": list(afm_parameters.get("grid_n", (-1, -1, -1))),
    }


def _translate_dft_params(common_parameters: dict, code_settings: dict) -> dict:
    protocol = common_parameters.get("protocol", "moderate")
    relax_type = common_parameters.get("relax_type", "none")
    engines = {
        "relax": _code_settings(code_settings),
    }
    return {
        "geom": {
            "engines": engines,
            "protocol": protocol,
            "relax_type": relax_type,
        },
        "tip": {
            "engines": engines,
            "protocol": protocol,
            "relax_type": "none",
        },
    }


def _translate_pp_params(code_settings: dict) -> dict:
    pp_engine = {
        "engines": {
            "pp": _code_settings(code_settings),
        }
    }
    return {
        "hartree_potential": {
            **pp_engine,
            "quantity": "potential",
        },
        "charge_density": {
            **pp_engine,
            "quantity": "charge_density",
        },
    }


def _translate_case(mode: str) -> str:
    if mode == "hartree":
        return AfmCase.HARTREE.name
    return AfmCase.EMPIRICAL.name


class AfmWorkChain(WorkChain):
    @classmethod
    def define(cls, spec):
        super().define(spec)
        spec.input_namespace("workgraph", dynamic=True)
        spec.outline(
            cls.run_workgraph,
            cls.results,
        )
        spec.output_namespace("results", dynamic=True)

    def run_workgraph(self):
        process = self.submit(WorkGraphEngine, **self.inputs.workgraph)
        return ToContext(workgraph_process=process)

    def results(self):
        for name, output in self.ctx.workgraph_process.outputs.items():
            self.out(f"results.{name}", output)


def get_builder(codes, structure, parameters, **kwargs):
    """Return the builder for the AFM workchain wrapper."""

    common_parameters = parameters.get("common", {})
    afm_parameters = parameters.get("afm", {})

    mode = afm_parameters.get("mode", "empirical")
    case = _translate_case(mode)

    relax = (
        "relax" in parameters.get("properties", [])
        and common_parameters.get("relax_type", "none") != "none"
    )

    scf_code = codes.get("scf", {})
    pp_code = codes.get("pp", {})

    wg = AfmWorkflow.build(
        engine=parameters.get("engine", "quantum_espresso"),
        case=case,
        structure=structure,
        afm_params=_translate_afm_params(afm_parameters),
        relax=relax,
        dft_params=_translate_dft_params(common_parameters, scf_code),
        pp_params=_translate_pp_params(pp_code) if pp_code.get("code") is not None else None,
        tip=kwargs.get("tip"),
    )

    builder = AfmWorkChain.get_builder()
    builder.workgraph = wg.to_dict() if hasattr(wg, "to_dict") else dict(wg)
    return builder


def update_inputs(_builder, _codes):
    """Update the inputs of the AFM workchain builder."""
    return


workchain_and_builder = {
    "workchain": AfmWorkChain,
    "exclude": ("structure",),
    "get_builder": get_builder,
    "update_inputs": update_inputs,
}
