from __future__ import annotations

import json
from pathlib import Path

import traitlets as tl
from importlib_resources import files
from jinja2 import Environment

from aiida import orm
from aiida.cmdline.utils.common import get_workchain_report
from aiida.orm.utils.serialize import deserialize_unsafe
from aiidalab_acwf.app.static import styles, templates
from aiidalab_acwf.common.time import format_time, relative_time
from aiidalab_acwf.parameters import DEFAULT_PARAMETERS

from .. import ResultsComponentModel

DEFAULT: dict = DEFAULT_PARAMETERS  # type: ignore

PERIODICITY_MAPPING = {
    (True, True, True): "xyz",
    (True, True, False): "xy",
    (True, False, False): "x",
    (False, False, False): "molecule",
}


class WorkflowSummaryModel(ResultsComponentModel):
    identifier = "workflow summary"

    failed_calculation_report = tl.Unicode("")

    has_failure_report = False

    @property
    def include(self):
        return True

    def generate_report_html(self):
        env = Environment()
        template = files(templates).joinpath("workflow_summary.jinja").read_text()
        parameters = self._generate_report_parameters()
        report = {key: value for key, value in parameters.items() if value}
        schema = json.load(Path(__file__).parent.joinpath("schema.json").open())
        return env.from_string(template).render(
            report=report,
            schema=schema,
            format=DEFAULT["summary_format"],
        )

    def generate_failure_report(self):
        if not (self.has_process and self.process.exit_status):
            return
        final_calcjob = self._get_final_calcjob(self.process)
        env = Environment()
        template = files(templates).joinpath("workflow_failure.jinja").read_text()
        style = files(styles).joinpath("style.css").read_text()
        self.failed_calculation_report = env.from_string(template).render(
            style=style,
            process_report=get_workchain_report(self.process, "REPORT"),
            calcjob_exit_message=final_calcjob.exit_message if final_calcjob else "N/A",
        )
        self.has_failure_report = True

    def _generate_report_parameters(self):
        if not self.process:
            return {}

        inputs = self.inputs
        if not inputs or not hasattr(inputs, "structure"):
            return {}

        structure: orm.StructureData = inputs.structure
        parameters = self._deserialize_extra("parameters")
        resources = self._deserialize_extra("resources")

        properties = parameters.get("properties", [])
        selected_plugins = [prop for prop in properties if prop != "relax"]
        plugin_name = selected_plugins[0] if selected_plugins else "none"

        ctime = self.process.ctime
        mtime = self.process.mtime

        report = {
            "workflow_properties": {
                "pk": self.process.pk,
                "uuid": str(self.process.uuid),
                "label": self.process.label,
                "description": self.process.description,
                "creation_time": f"{format_time(ctime)} ({relative_time(ctime)})",
                "modification_time": f"{format_time(mtime)} ({relative_time(mtime)})",
                "process_state": (
                    self.process.process_state.value if self.process.process_state else "unknown"
                ),
                "exit_status": self.process.exit_status
                if self.process.is_terminated
                else "running",
                "exit_message": self.process.exit_message or "",
            },
            "initial_structure_properties": {
                "structure_pk": structure.pk,
                "structure_uuid": str(structure.uuid),
                "formula": structure.get_formula(),
                "num_atoms": len(structure.sites),
                "periodicity": PERIODICITY_MAPPING.get(structure.pbc, "xyz"),
                "cell_lengths": "{:.3f} {:.3f} {:.3f}".format(*structure.cell_lengths),
                "cell_angles": "{:.0f} {:.0f} {:.0f}".format(*structure.cell_angles),
                **self._get_symmetry_group_info(structure),
            },
            "workflow_settings": {
                "engine": resources.get("engine"),
                "selected_properties": ", ".join(selected_plugins),
                "protocol": parameters.get("common", {}).get("protocol"),
                "relax_type": parameters.get("common", {}).get("relax_type"),
                "spin_type": parameters.get("common", {}).get("spin_type"),
                "electronic_type": parameters.get("common", {}).get("electronic_type"),
            },
            "plugin_settings": {
                "plugin": plugin_name,
            },
        }

        plugin_params = parameters.get(plugin_name, {}) if plugin_name != "none" else {}
        if plugin_name == "afm":
            report["plugin_settings"] |= {
                "mode": plugin_params.get("mode"),
                "tip": plugin_params.get("tip"),
                "charge": plugin_params.get("charge"),
                "klat": plugin_params.get("klat"),
                "scan_min": self._join_vector(plugin_params.get("scan_min")),
                "scan_max": self._join_vector(plugin_params.get("scan_max")),
                "scan_step": self._join_vector(plugin_params.get("scan_step")),
            }

        return {
            section: {k: v for k, v in values.items() if v not in (None, "")}
            for section, values in report.items()
        }

    def _deserialize_extra(self, key: str) -> dict:
        value = self.process.base.extras.get(key, {})
        if isinstance(value, str):
            value = deserialize_unsafe(value)
        return value if isinstance(value, dict) else {}

    @staticmethod
    def _join_vector(value):
        if not isinstance(value, (list, tuple)):
            return None
        return " ".join(str(item) for item in value)

    def _get_symmetry_group_info(self, structure: orm.StructureData) -> dict:
        if any(structure.pbc):
            return self._get_pymatgen_structure(structure)
        return self._get_pymatgen_molecule(structure)

    @staticmethod
    def _get_pymatgen_structure(structure: orm.StructureData) -> dict:
        from pymatgen.symmetry.analyzer import SpacegroupAnalyzer

        clone = structure.clone()
        clone.pbc = (True, True, True)
        analyzer = SpacegroupAnalyzer(structure=clone.get_pymatgen_structure())
        symbol = analyzer.get_space_group_symbol()
        number = analyzer.get_space_group_number()
        return {"space_group": f"{symbol} ({number})"}

    @staticmethod
    def _get_pymatgen_molecule(structure: orm.StructureData) -> dict:
        from pymatgen.symmetry.analyzer import PointGroupAnalyzer

        analyzer = PointGroupAnalyzer(mol=structure.get_pymatgen_molecule())
        return {"point_group": analyzer.get_pointgroup()}

    @staticmethod
    def _get_final_calcjob(node: orm.WorkChainNode) -> orm.CalcJobNode | None:
        try:
            return [
                process
                for process in node.called_descendants
                if isinstance(process, orm.CalcJobNode) and process.is_finished
            ][-1]
        except IndexError:
            return None
