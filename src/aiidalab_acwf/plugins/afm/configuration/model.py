import traitlets as tl

from aiidalab_acwf.common.panel import ConfigurationSettingsModel, PluginOutline


class AfmPluginOutline(PluginOutline):
    title = "Atomic force microscopy (AFM)"


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

    def get_model_state(self) -> dict:
        return {
            "mode": self.mode,
            "pbc": self.pbc,
            "grid_n": (self.grid_nx, self.grid_ny, self.grid_nz),
            "grid_a": (self.grid_ax, self.grid_ay, self.grid_az),
            "grid_b": (self.grid_bx, self.grid_by, self.grid_bz),
            "grid_c": (self.grid_cx, self.grid_cy, self.grid_cz),
            "probe_type": self.probe_type,
            "charge": self.charge,
            "r0_probe": (self.r0_probe_x, self.r0_probe_y, self.r0_probe_z),
            "tip": self.tip,
            "klat": self.klat,
            "krad": self.krad,
            "sigma": self.sigma,
            "scan_step": (self.scan_step_x, self.scan_step_y, self.scan_step_z),
            "scan_min": (self.scan_min_x, self.scan_min_y, self.scan_min_z),
            "scan_max": (self.scan_max_x, self.scan_max_y, self.scan_max_z),
            "f0_cantilever": self.f0_cantilever,
            "amplitude": self.amplitude,
        }

    def set_model_state(self, state: dict):
        self.mode = state.get("mode", self.mode)
        self.pbc = state.get("pbc", self.pbc)
        (
            self.grid_nx,
            self.grid_ny,
            self.grid_nz,
        ) = state.get("grid_n", (self.grid_nx, self.grid_ny, self.grid_nz))
        (
            self.grid_ax,
            self.grid_ay,
            self.grid_az,
        ) = state.get("grid_a", (self.grid_ax, self.grid_ay, self.grid_az))
        (
            self.grid_bx,
            self.grid_by,
            self.grid_bz,
        ) = state.get("grid_b", (self.grid_bx, self.grid_by, self.grid_bz))
        (
            self.grid_cx,
            self.grid_cy,
            self.grid_cz,
        ) = state.get("grid_c", (self.grid_cx, self.grid_cy, self.grid_cz))
        self.probe_type = state.get("probe_type", self.probe_type)
        self.charge = state.get("charge", self.charge)
        (
            self.r0_probe_x,
            self.r0_probe_y,
            self.r0_probe_z,
        ) = state.get("r0_probe", (self.r0_probe_x, self.r0_probe_y, self.r0_probe_z))
        self.tip = state.get("tip", self.tip)
        self.klat = state.get("klat", self.klat)
        self.krad = state.get("krad", self.krad)
        self.sigma = state.get("sigma", self.sigma)
        (
            self.scan_step_x,
            self.scan_step_y,
            self.scan_step_z,
        ) = state.get("scan_step", (self.scan_step_x, self.scan_step_y, self.scan_step_z))
        (
            self.scan_min_x,
            self.scan_min_y,
            self.scan_min_z,
        ) = state.get("scan_min", (self.scan_min_x, self.scan_min_y, self.scan_min_z))
        (
            self.scan_max_x,
            self.scan_max_y,
            self.scan_max_z,
        ) = state.get("scan_max", (self.scan_max_x, self.scan_max_y, self.scan_max_z))
        self.f0_cantilever = state.get("f0_cantilever", self.f0_cantilever)
        self.amplitude = state.get("amplitude", self.amplitude)
