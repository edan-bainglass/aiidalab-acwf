import ipywidgets as ipw

from aiidalab_acwf.common.infobox import InAppGuide
from aiidalab_acwf.common.panel import ConfigurationSettingsPanel

from .model import AfmConfigurationSettingsModel


class AfmConfigurationSettingsPanel(ConfigurationSettingsPanel[AfmConfigurationSettingsModel]):
    def render(self):
        if self.rendered:
            return

        mode = ipw.ToggleButtons(description="AFM simulation mode")
        ipw.dlink((self._model, "mode_options"), (mode, "options"))
        ipw.link((self._model, "mode"), (mode, "value"))

        pbc = ipw.Checkbox(description="Periodic boundary conditions")
        ipw.link((self._model, "pbc"), (pbc, "value"))

        grid_nx = ipw.IntText()
        ipw.link((self._model, "grid_nx"), (grid_nx, "value"))
        grid_ny = ipw.IntText()
        ipw.link((self._model, "grid_ny"), (grid_ny, "value"))
        grid_nz = ipw.IntText()
        ipw.link((self._model, "grid_nz"), (grid_nz, "value"))
        grid_n_label = ipw.Label("Force field sampling")
        grid_n = ipw.HBox([grid_n_label, grid_nx, grid_ny, grid_nz])
        grid_n.add_class("vector-hbox")

        grid_ax = ipw.FloatText()
        ipw.link((self._model, "grid_ax"), (grid_ax, "value"))
        grid_ay = ipw.FloatText()
        ipw.link((self._model, "grid_ay"), (grid_ay, "value"))
        grid_az = ipw.FloatText()
        ipw.link((self._model, "grid_az"), (grid_az, "value"))
        grid_a_label = ipw.Label("Grid vector A (Å)")
        grid_a = ipw.HBox([grid_a_label, grid_ax, grid_ay, grid_az])
        grid_a.add_class("vector-hbox")

        grid_bx = ipw.FloatText()
        ipw.link((self._model, "grid_bx"), (grid_bx, "value"))
        grid_by = ipw.FloatText()
        ipw.link((self._model, "grid_by"), (grid_by, "value"))
        grid_bz = ipw.FloatText()
        ipw.link((self._model, "grid_bz"), (grid_bz, "value"))
        grid_b_label = ipw.Label("Grid vector B (Å)")
        grid_b = ipw.HBox([grid_b_label, grid_bx, grid_by, grid_bz])
        grid_b.add_class("vector-hbox")

        grid_cx = ipw.FloatText()
        ipw.link((self._model, "grid_cx"), (grid_cx, "value"))
        grid_cy = ipw.FloatText()
        ipw.link((self._model, "grid_cy"), (grid_cy, "value"))
        grid_cz = ipw.FloatText()
        ipw.link((self._model, "grid_cz"), (grid_cz, "value"))
        grid_c_label = ipw.Label("Grid vector C (Å)")
        grid_c = ipw.HBox([grid_c_label, grid_cx, grid_cy, grid_cz])
        grid_c.add_class("vector-hbox")

        probe_type = ipw.Dropdown(description="Probe type")
        ipw.dlink((self._model, "probe_type_options"), (probe_type, "options"))
        ipw.link((self._model, "probe_type"), (probe_type, "value"))

        charge = ipw.FloatText(description="Charge (e)")
        ipw.link((self._model, "charge"), (charge, "value"))

        r0_probe_x = ipw.FloatText()
        ipw.link((self._model, "r0_probe_x"), (r0_probe_x, "value"))
        r0_probe_y = ipw.FloatText()
        ipw.link((self._model, "r0_probe_y"), (r0_probe_y, "value"))
        r0_probe_z = ipw.FloatText()
        ipw.link((self._model, "r0_probe_z"), (r0_probe_z, "value"))
        r0_probe_label = ipw.Label("Probe position (Å)")
        r0_probe = ipw.HBox([r0_probe_label, r0_probe_x, r0_probe_y, r0_probe_z])
        r0_probe.add_class("vector-hbox")

        tip = ipw.Dropdown(description="Tip")
        ipw.dlink((self._model, "tip_options"), (tip, "options"))
        ipw.link((self._model, "tip"), (tip, "value"))

        klat = ipw.FloatText(description="Lateral stiffness (N/m)")
        ipw.link((self._model, "klat"), (klat, "value"))

        krad = ipw.FloatText(description="Radial stiffness (N/m)")
        ipw.link((self._model, "krad"), (krad, "value"))

        sigma = ipw.FloatText(description="Sigma")
        ipw.link((self._model, "sigma"), (sigma, "value"))

        scan_step_x = ipw.FloatText()
        ipw.link((self._model, "scan_step_x"), (scan_step_x, "value"))
        scan_step_y = ipw.FloatText()
        ipw.link((self._model, "scan_step_y"), (scan_step_y, "value"))
        scan_step_z = ipw.FloatText()
        ipw.link((self._model, "scan_step_z"), (scan_step_z, "value"))
        scan_step_label = ipw.Label("Scan step (Å)")
        scan_step = ipw.HBox([scan_step_label, scan_step_x, scan_step_y, scan_step_z])
        scan_step.add_class("vector-hbox")

        scan_min_x = ipw.FloatText()
        ipw.link((self._model, "scan_min_x"), (scan_min_x, "value"))
        scan_min_y = ipw.FloatText()
        ipw.link((self._model, "scan_min_y"), (scan_min_y, "value"))
        scan_min_z = ipw.FloatText()
        ipw.link((self._model, "scan_min_z"), (scan_min_z, "value"))
        scan_min_label = ipw.Label("Scan min (Å)")
        scan_min = ipw.HBox([scan_min_label, scan_min_x, scan_min_y, scan_min_z])
        scan_min.add_class("vector-hbox")

        scan_max_x = ipw.FloatText()
        ipw.link((self._model, "scan_max_x"), (scan_max_x, "value"))
        scan_max_y = ipw.FloatText()
        ipw.link((self._model, "scan_max_y"), (scan_max_y, "value"))
        scan_max_z = ipw.FloatText()
        ipw.link((self._model, "scan_max_z"), (scan_max_z, "value"))
        scan_max_label = ipw.Label("Scan max (Å)")
        scan_max = ipw.HBox([scan_max_label, scan_max_x, scan_max_y, scan_max_z])
        scan_max.add_class("vector-hbox")

        f0_cantilever = ipw.FloatText(description="Cantilever frequency (Hz)")
        ipw.link((self._model, "f0_cantilever"), (f0_cantilever, "value"))

        amplitude = ipw.FloatText(description="Amplitude (Å)")
        ipw.link((self._model, "amplitude"), (amplitude, "value"))

        self.children = [
            InAppGuide(identifier="afm-configuration-settings"),
            mode,
            ipw.HTML("<h3>Force-field grid parameters</h3>"),
            pbc,
            grid_n,
            grid_a,
            grid_b,
            grid_c,
            ipw.HTML("<h3>Tip parameters</h3>"),
            probe_type,
            charge,
            r0_probe,
            tip,
            klat,
            krad,
            sigma,
            ipw.HTML("<h3>Scan parameters</h3>"),
            scan_step,
            scan_min,
            scan_max,
            ipw.HTML("<h3>Conversion parameters Fz → df</h3>"),
            f0_cantilever,
            amplitude,
        ]

        self.rendered = True
        self.add_class("afm-configuration-settings-panel")
