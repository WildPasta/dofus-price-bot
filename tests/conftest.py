# Python Standard Library Imports
import os
import sys
from pathlib import Path

# Third-Party Imports
import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]

# __main__.py imports "gui.gui" as a top-level package, which matches the layout
# of the installed wheel. Add both directories to sys.path so the tests work
# straight from a repository checkout, without building/installing first.
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / "dofus_cookbot"))


def pytest_configure(config):
    config.addinivalue_line(
        "markers",
        "needs_display: test drives the screen/mouse stack and requires a display "
        "(on Linux run the suite with xvfb-run)",
    )


def pytest_collection_modifyitems(config, items):
    """Skip display-dependent tests when running headless on Linux (no $DISPLAY)."""
    if sys.platform != "linux" or os.environ.get("DISPLAY"):
        return

    skip_marker = pytest.mark.skip(
        reason="no $DISPLAY available; run with xvfb-run to include this test"
    )
    for item in items:
        if "needs_display" in item.keywords:
            item.add_marker(skip_marker)
