from aiida import orm
from aiida.engine import WorkChain


class AfmWorkChain(WorkChain):
    @classmethod
    def define(cls, spec):
        super().define(spec)
        spec.input(
            "structure",
            valid_type=orm.StructureData,
            help="The input structure.",
        )
        spec.input(
            "parameters",
            valid_type=orm.Dict,
            help="The input parameters.",
        )


def get_builder(codes, structure, parameters, **kwargs):
    """Return the builder for the AFM workchain."""


def update_inputs(builder, codes):
    """Update the inputs of the AFM workchain builder."""


workchain_and_builder = {
    "workchain": AfmWorkChain,
    "exclude": ("structure"),
    "get_builder": get_builder,
    "update_inputs": update_inputs,
}
