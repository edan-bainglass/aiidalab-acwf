import traitlets as tl

from aiidalab_acwf.common.panel import (
    ConfigurationSettingsModel,
)


class AfmConfigurationSettingsModel(ConfigurationSettingsModel):
    """Model for the AFM configuration settings."""

    title = "AFM"
    identifier = "afm"

    # Partial list from:
    # https://github.com/Probe-Particle/ppafm/wiki/Setting-simulation-parameters

    # Mode
    mode_options = tl.List(
        tl.Tuple(tl.Unicode(), tl.Unicode()),
        [
            ("Empirical", "empirical"),
            ("Hartree", "hartree"),
        ],
    )
    mode = tl.Unicode("empirical")

    # Force-field grid parameters
    pbc = tl.Bool(True)
    grid_nx = tl.Int(-1)
    grid_ny = tl.Int(-1)
    grid_nz = tl.Int(-1)
    grid_ax = tl.Float(20.0)
    grid_ay = tl.Float(0.0)
    grid_az = tl.Float(0.0)
    grid_bx = tl.Float(0.0)
    grid_by = tl.Float(20.0)
    grid_bz = tl.Float(0.0)
    grid_cx = tl.Float(0.0)
    grid_cy = tl.Float(0.0)
    grid_cz = tl.Float(20.0)

    # Tip parameters
    probe_type_options = tl.List(tl.Unicode(), ["O", "CO"])
    probe_type = tl.Unicode("O")
    charge = tl.Float(0.0)
    r0_probe_x = tl.Float(0.0)
    r0_probe_y = tl.Float(0.0)
    r0_probe_z = tl.Float(4.0)
    tip_options = tl.List(tl.Unicode(), ["s", "pz", "dz2"])
    tip: tl.Unicode = tl.Unicode("s")
    klat = tl.Float(0.5)
    krad = tl.Float(20.0)
    sigma = tl.Float(0.7)

    # Scan parameters
    scan_step_x = tl.Float(20.0)
    scan_step_y = tl.Float(20.0)
    scan_step_z = tl.Float(8.0)
    scan_min_x = tl.Float(0.0)
    scan_min_y = tl.Float(0.0)
    scan_min_z = tl.Float(5.0)
    scan_max_x = tl.Float(0.1)
    scan_max_y = tl.Float(0.1)
    scan_max_z = tl.Float(0.1)

    # Conversion parameters Fz -> df
    f0_cantilever = tl.Float(30300.0)
    amplitude = tl.Float(1.0)
