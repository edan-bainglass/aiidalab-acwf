import ipywidgets as ipw


def get_start_widget(appbase, jupbase, notebase):  # noqa: ARG001
    return ipw.HTML(f"""
        <div class="app-container">
            <a
                class="logo"
                href="{appbase}/acwf.ipynb"
                target="_blank"
            >
                <img src="https://aiida-common-workflows.readthedocs.io/en/latest/_images/calculator.jpg" alt="AiiDA Common Workflows" width="200">
            </a>
        </div>
    """)
