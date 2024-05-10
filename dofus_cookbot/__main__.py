##########
# Author: wildpasta
# Description: Core of Dofus Cooker, handle GUI, autoclick, OCR, and JSON parsing
# Usage: python main.py
# Example: python main.py
##########

# Python Standard Library Imports
from datetime import datetime
import json
import os
from random import uniform
from time import sleep
import sys

# Third-Party Imports
try:
    from PIL import Image, ImageFilter
    from prettytable import PrettyTable
    from pynput.keyboard import Key
    from pynput.mouse import Button as pybtn
    import pyautogui
    import pynput
    import pytesseract
    import pyscreenshot as ImageGrab
except ModuleNotFoundError as e:
    print(f"ModuleNotFoundError: {e}")
    print("Please install the required modules using the following command:")
    print("pip install -r requirements.txt")
    sys.exit(1)

# Local/Application Specific Imports
from gui.gui import create_window, ending_message

mouse = pynput.mouse.Controller()
keyboard = pynput.keyboard.Controller()
pytesseract.pytesseract.tesseract_cmd = r'C:\\Users\\Richard\\AppData\\Local\\Programs\\Tesseract-OCR\\tesseract.exe'

def do_click(x: int, y: int) -> None:
    """
    purpose:
        Perform a mouse click at the specified coordinates
    input:
        nb (int): Number of clicks to perform
        x (int) : X coordinate of the click
        y (int) : Y coordinate of the click
    output:
        None
    """

    try:
        width, height = pyautogui.size()  # Get the screen resolution
        x = int(x * width / 2560)  # Convert x coordinate to match screen resolution
        y = int(y * height / 1440)  # Convert y coordinate to match screen resolution
        
        delay = round(uniform(0, 1), 2)
        sleep(delay)  # sleep between 2 and 3 seconds

        pyautogui.moveTo(x, y)
        delay = round(uniform(100, 300), 2) / 1000.0
        sleep(delay)  # between 100 and 300 ms
        pyautogui.click()

    except Exception as e:
        print(f"Error when clicking: {e}")

def apply_filter_on_image(input_image_path, output_image_path):
    """
    purpose:
        Apply a thresholding filter on an image
    input:
        input_image_path (str): Path to the input image
        output_image_path (str): Path to save the output image
    output:
        None
    """

    try:
        input_image = Image.open(input_image_path)

        # thresholding filter
        threshold = 127  # luminosity threshold (0-255)
        output_image = input_image.convert("L").point(lambda pixel: 255 if pixel > threshold else 0)

        output_image.save(output_image_path)

    except Exception as e:
        print(f"Error when applying filter on screenshot: {e}")

def process_image(screenshot: Image.Image, item_name: str) -> str:
    """
    purpose:
        Process the screenshot of the item's price
    input:
        screenshot (Image): screenshot of the item's price
        item_name (str): name of the item
    output:
        item_current_price (str): price of the item
    """

    try:
        # Save the screenshot within img folder
        timestamp = datetime.now()
        timestamp = timestamp.strftime("%Y%m%d%H%M%S")
        os.makedirs("img", exist_ok=True)    

        filename = f"img/{item_name}-{timestamp}.png"
        screenshot.save(filename)

        filtered_filename = f"img/{item_name}-{timestamp}_filtered.png"
        apply_filter_on_image(filename, filtered_filename)
        
        # process the screenshot
        item_img = Image.open(filtered_filename)
        text = pytesseract.image_to_string(item_img)
        try:
            item_current_price = int(''.join(filter(str.isdigit, text)))
        except:
            item_current_price = 1
        
        # Delete the screenshot
        os.remove(filename)
        os.remove(filtered_filename)

        return item_current_price
    
    except Exception as e:
        print(f"Error with OCR recognition: {e}")

def determine_price(item_name: str, item_quantity: int, item_type: str, item_lvl: int) -> dict:
    """
    purpose:
        Use OCR to determine the price of an item in Dofus
    input:
        item_name (str)    : name of the item to search for
        item_quantity (int): quantity of the item required
        item_type (str)    : type of the item
        item_lvl (int)     : level of the item
    output:
        dict: Dictionary containing the price of the item
    """

    # click: clear research
    do_click(759, 268)
    sleep(0.2)

    # click: searchbar
    do_click(555, 264)
    sleep(0.2)

    # keyboard: write the item name in searchbar
    keyboard.type(item_name)
    sleep(0.7)

    # click: first item to unwrap prices
    do_click(856, 305)
    sleep(1)

    # take screenshot of average price
    # x_top_left, y_top_left, x_bottom_right, y_bottom_right
    screenshot = ImageGrab.grab(bbox=(1220, 350, 1375, 390))
    item_current_price = process_image(screenshot, item_name)

    print(f"Price found ! 1 x {item_name} for {item_current_price} Kamas")

    return {'price': item_current_price}

def parse_recipe_from_json(json_data: list, item_name: str) -> list:
    """
    purpose:
        Parse the JSON data to retrieve the name and level of the specified item's recipe ingredients
    input:
        json_data (list): JSON data containing item information
        item_name (str) : name of the item to search for
    output:
        list: list of dictionaries containing the name, quantity, and level of the recipe ingredients
    """

    try:
        parsed_recipe = []
        for item_data in json_data:
            if item_data['name'] == item_name:
                for recipe_item in item_data.get('recipe', []):
                    for ingredient_name, ingredient_info in recipe_item.items():
                        parsed_recipe.append({
                            'name': ingredient_name,
                            'type': ingredient_info['type'],
                            'quantity': int(ingredient_info['quantity']),
                            'level': int(ingredient_info['lvl'])
                        })
                break  # Exit loop once the item's recipe is found
        return parsed_recipe
    
    except Exception as e:
        print(f"Error when parsing recipe from JSON: {e}")

def create_report(target: str, parsed_recipe: list) -> None:
    """
    purpose:
        Create a report containing the recipe details for the target item
    input:
        target (str)        : name of the target item
        parsed_recipe (list): list of dictionaries containing the recipe details
    output:
        None
    """

    table = PrettyTable()
    table.field_names = [target, "Level", "Quantity", "Price", "Total Price"]
    total_price_all_items = 0 

    for resource in parsed_recipe:
        item_name = resource['name']
        item_lvl = resource['level']
        item_quantity = resource['quantity']
        item_price = resource['price']

        total_price = item_quantity * item_price
        total_price_all_items += total_price

        table.add_row([item_name, item_lvl, item_quantity, item_price, total_price])

    # Add 20% tax
    tax = round(total_price_all_items * 0.20)
    total_price_with_tax = total_price_all_items + tax

    # Print total price with tax
    table.add_row(["-" * 10, "-" * 10, "-" * 10, "-" * 10, "-" * 10])
    table.add_row(["Total Price (w/ taxes)", "", "", "", total_price_with_tax])

    print(table)

def main():
    # Pop the GUI to select items
    target_lst = create_window()

    # Load JSON data from file
    recipe_path = "res/equipment_recipes.json"
    with open(recipe_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    for target in target_lst:
        parsed_recipe = parse_recipe_from_json(data, target)
        if not parsed_recipe:
            print("No recipe found. Exiting...")
            sys.exit(1)
        
        for resource in parsed_recipe:
            item_name = resource['name']
            item_quantity = resource['quantity']
            item_type = resource['type']
            item_lvl = resource['level']

            price_info = determine_price(item_name, item_quantity, item_type, item_lvl)
            resource.update(price_info)

        # Create table report for the item
        create_report(target, parsed_recipe)

    ending_message()

if __name__ == "__main__":  
    main()