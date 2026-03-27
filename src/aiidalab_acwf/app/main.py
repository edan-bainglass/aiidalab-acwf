from __future__ import annotations

import typing as t
from pathlib import Path

import ipywidgets as ipw
from IPython.display import display

from aiida import orm
from aiidalab_widgets_base.utils.loaders import load_css

from .app import AppController, AppModel, AppView
from .static import styles


class AcwfApp:
    def __init__(self, url_query: dict[str, t.Any] | None = None):
        # HACK somehow resolves https://github.com/aiidalab/aiidalab-qe/issues/1356
        # TODO investigate why this is needed and how it resolves the issue
        _ = orm.User.collection.get_default().email

        url_query = url_query or {}

        pk = url_query.get("pk", [None])[0]

        self.process = pk

        self._load_styles()

        self.model = AppModel()
        self.view = AppView()
        display(self.view)

        self.controller = AppController(self.model, self.view)
        self.controller.enable_toggles()

        if not self.model.validate_process(pk):
            self.view.app_container.children = [
                ipw.HTML(f"""
                    <div class="alert alert-danger" style="text-align: center">
                        Process {pk} does not exist
                        <br>
                        Please visit the <b>Calculation history</b> page to view
                        existing processes
                    </div>
                """)
            ]
        else:
            self.controller.load_wizard(duplicating="duplicating" in url_query)

    def _load_styles(self):
        """Load CSS styles from the static directory."""
        load_css(css_path=Path(styles.__file__).parent)
