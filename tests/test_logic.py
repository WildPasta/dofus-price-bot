# Python Standard Library Imports
import importlib
import json

# Third-Party Imports
import pytest

# importing __main__.py loads the GUI automation stack (pyautogui, pynput...)
pytestmark = pytest.mark.needs_display


@pytest.fixture(scope="module")
def core():
    """Import __main__ lazily so headless test collection does not crash."""
    return importlib.import_module("dofus_cookbot.__main__")


@pytest.fixture(scope="module")
def recipe_data():
    """Load the recipe database bundled with the package, like main() does."""
    from importlib.resources import files

    with files("dofus_cookbot.res").joinpath("equipment_recipes.json").open(
        encoding="utf-8"
    ) as f:
        return json.loads(f.read())


def test_parse_recipe_from_bundled_data(core, recipe_data):
    parsed = core.parse_recipe_from_json(recipe_data, "Coiffe du Comte Harebourg")

    assert len(parsed) == 8  # recipe of the first item of the database

    first = parsed[0]
    assert first["name"] == "Galet brasillant"
    assert first["type"] == "Galet"
    assert first["level"] == 150  # JSON stores strings, parser converts to int
    assert first["quantity"] == 3


def test_parse_recipe_unknown_item_returns_empty_list(core, recipe_data):
    assert core.parse_recipe_from_json(recipe_data, "Item qui n'existe pas") == []


def test_create_report_prints_totals_with_tax(core, capsys):
    parsed_recipe = [
        {"name": "Ressource A", "level": 100, "quantity": 2, "price": 100},
        {"name": "Ressource B", "level": 50, "quantity": 3, "price": 50},
    ]

    core.create_report("Item cible", parsed_recipe)
    output = capsys.readouterr().out

    # 2*100 + 3*50 = 350 kamas; the report prints the total with 20% tax = 420
    for expected in ("Ressource A", "Ressource B", "200", "150", "420"):
        assert expected in output
