# Python Standard Library Imports
import importlib.metadata
from io import BytesIO
from pathlib import Path
from urllib.parse import unquote

# Third-Party Imports
import pytest

import PIL
import prettytable
import pytesseract
import requests

REQUIREMENTS_FILE = Path(__file__).resolve().parents[1] / "requirements.txt"


def pinned_requirements() -> dict:
    """Parse requirements.txt into a {package: version} dictionary."""
    pins = {}
    for line in REQUIREMENTS_FILE.read_text().splitlines():
        if "==" in line:
            package, version = line.split("==")
            pins[package.strip().lower()] = version.strip()
    return pins


@pytest.mark.parametrize("package, version", sorted(pinned_requirements().items()))
def test_pinned_version_is_installed(package, version):
    """The installed version must match the requirements.txt pin exactly."""
    assert importlib.metadata.version(package) == version


def test_requirements_and_pyproject_pins_match():
    """requirements.txt and pyproject.toml must declare the same pins."""
    pyproject = (REQUIREMENTS_FILE.parent / "pyproject.toml").read_text().lower()

    for package, version in pinned_requirements().items():
        assert f"{package}=={version}" in pyproject, (
            f"{package}=={version} is missing or different in pyproject.toml"
        )


def test_pillow_create_filter_reload_image():
    """Pillow must handle the image pipeline used by process_image()."""
    from PIL import Image, ImageFilter  # noqa: F401  (same imports as __main__.py)

    image = Image.new("RGB", (64, 32), color=(255, 0, 0))
    image = image.filter(ImageFilter.GaussianBlur(2))

    buffer = BytesIO()
    image.save(buffer, format="PNG")
    buffer.seek(0)

    reloaded = Image.open(buffer)
    assert reloaded.size == (64, 32)
    assert reloaded.getpixel((32, 16))[0] > 200  # still mostly red


def test_prettytable_renders_report():
    """PrettyTable must render the report table built by create_report()."""
    table = prettytable.PrettyTable()
    table.field_names = ["Item", "Level", "Quantity", "Price", "Total Price"]
    table.add_row(["Galet brasillant", 150, 3, 1000, 3000])

    rendered = table.get_string()
    for expected in ("Galet brasillant", "150", "1000", "3000"):
        assert expected in rendered


def test_requests_prepares_dofusdb_request():
    """requests must build the GET requests sent by utils/api/api.py."""
    url = "https://api.dofusdb.fr/items?slug.fr[$search]=galet"
    request = requests.Request(
        "GET", url, headers={"User-Agent": "dofus-price-bot-tests"}
    ).prepare()

    assert unquote(request.url) == url
    assert request.headers["User-Agent"] == "dofus-price-bot-tests"


def test_pytesseract_exposes_ocr_entry_point():
    """pytesseract must expose the OCR call used by process_image()."""
    assert callable(pytesseract.image_to_string)


@pytest.mark.needs_display
def test_screen_automation_stack_works():
    """The GUI automation stack imported by __main__.py must be usable."""
    import pyautogui
    import pynput
    import pyscreenshot as ImageGrab  # noqa: F401  (same imports as __main__.py)

    width, height = pyautogui.size()
    assert width > 0 and height > 0

    # __main__.py instantiates both controllers at import time
    pynput.mouse.Controller()
    pynput.keyboard.Controller()

    screenshot = ImageGrab.grab(bbox=(0, 0, 10, 10))
    assert screenshot.size == (10, 10)
