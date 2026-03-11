import traitlets as tl


class AppModel(tl.HasTraits):
    """Model class for the AiiDAlab ACWF app."""

    workflow = tl.Unicode(
        help="The selected workflow. This is a string that identifies the workflow, e.g., 'afm-scan'.",
    ).tag(sync=True)

    workflow_options = tl.List(
        trait=tl.Tuple(tl.Unicode(), tl.Unicode()),
        help="A list of available workflows. This list is used to populate the workflow selector dropdown.",
    ).tag(sync=True)

    structure_uuid = tl.Unicode(
        "",
        help="The UUID of the structure to be used as input for the workflow.",
    ).tag(sync=True)

    workflow_parameters = tl.Dict(
        default_value={},
        help="A dictionary containing the workflow parameters. The keys and values of this dictionary depend on the selected workflow.",
    ).tag(sync=True)

    quantum_engine = tl.Unicode(
        help="The selected quantum engine. This is a string that identifies the quantum engine, e.g., 'quantum-espresso'.",
    ).tag(sync=True)

    quantum_engine_options = tl.List(
        trait=tl.Tuple(tl.Unicode(), tl.Unicode()),
        help="A list of available quantum engines. This list is used to populate the quantum engine selector dropdown.",
    ).tag(sync=True)

    computational_resources = tl.Dict(
        default_value={},
        help="A dictionary containing the computational resources configuration. The keys and values of this dictionary depend on the available resources and the requirements of the selected workflow.",
    ).tag(sync=True)

    workflow_label = tl.Unicode(
        "",
        help="A user-friendly label for the workflow, e.g., 'AFM Scan'.",
    ).tag(sync=True)

    workflow_description = tl.Unicode(
        "",
        help="A brief description of the workflow.",
    ).tag(sync=True)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.workflow_options = self._fetch_workflows()
        self.quantum_engine_options = self._fetch_quantum_engines()

    @property
    def structure(self):
        """Return the structure associated with the current structure UUID."""
        from aiida.common.exceptions import NotExistent
        from aiida.orm import load_node

        if not self.structure_uuid:
            return None
        try:
            return load_node(self.structure_uuid)
        except NotExistent:
            return None

    def _fetch_workflows(self):
        """Fetch the available workflows from the AiiDAlab environment."""
        # This is a placeholder implementation. In a real implementation, this method would query the AiiDAlab environment for available workflows.
        return [
            ("Select a workflow", ""),
            ("AFM scan", "afm-scan"),
            ("Geometry optimization", "geometry-optimization"),
            ("Molecular dynamics", "molecular-dynamics"),
        ]

    def _fetch_quantum_engines(self):
        """Fetch the available quantum engines from the AiiDAlab environment."""
        # This is a placeholder implementation. In a real implementation, this method would query the AiiDAlab environment for available quantum engines.
        return [
            ("Select a code", ""),
            ("Quantum ESPRESSO", "quantum-espresso"),
            ("VASP", "vasp"),
            ("CP2K", "cp2k"),
        ]
