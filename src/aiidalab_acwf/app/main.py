import ipywidgets as ipw


class AcwfApp(ipw.VBox):
    def __init__(self, children=..., **kwargs):
        super().__init__(children, **kwargs)

    def load(self):
        print("Loading the AiiDA Common Workflows (ACWF) app...")
