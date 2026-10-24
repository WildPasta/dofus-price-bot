# Third-Party Imports
from dofus_cookbot.gui.gui import get_item_names


def test_get_item_names_returns_sorted_names_from_bundled_recipes():
    names = get_item_names("equipment_recipes.json")

    assert len(names) > 0
    assert names == sorted(names)
