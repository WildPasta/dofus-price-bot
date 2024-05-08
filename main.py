import os
import pynput
import pytesseract
from datetime import datetime
from gui import *
from PIL import Image, ImageFilter
from prettytable import PrettyTable
from pynput.mouse import Button as pybtn
from pynput.keyboard import Key
import pyscreenshot as ImageGrab
from random import uniform
from time import sleep
import pyautogui
import sys

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

    width, height = pyautogui.size()  # Get the screen resolution
    x = int(x * width / 2560)  # Convert x coordinate to match screen resolution
    y = int(y * height / 1440)  # Convert y coordinate to match screen resolution
    
    delay = round(uniform(0, 1), 2)
    sleep(delay)  # between 2 and 3 s

    pyautogui.moveTo(x, y)  # Move the mouse to the adjusted coordinates
    delay = round(uniform(100, 300), 2) / 1000.0  # Convert to milliseconds
    sleep(delay)  # between 100 and 300 ms
    pyautogui.click()

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
    input_image = Image.open(input_image_path)

    # thresholding filter
    threshold = 127  # luminosity threshold (0-255)
    output_image = input_image.convert("L").point(lambda pixel: 255 if pixel > threshold else 0)

    output_image.save(output_image_path)

def ocr_determine_price(item_name: str, item_quantity: int, item_type: str, item_lvl: int) -> dict:
    """
    purpose:
        Use OCR to determine the price of an item in Dofus
    input:
        item_name (str)    : The name of the item to search for
        item_quantity (int): The quantity of the item required
        item_type (str)    : The type of the item
        item_lvl (int)     : The level of the item
    output:
        dict: Dictionary containing the price of the item
    """

    now = datetime.now()
    now = now.strftime("%Y%m%d%H%M%S")

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

    ##############
    ## PUT THAT IN A FUNCTION ##
    # take screenshot of average price
    # x_top_left, y_top_left, x_bottom_right, y_bottom_right
    im = ImageGrab.grab(bbox=(1220, 350, 1375, 390))

    filename = f"{item_name}-{now}.png"
    im.save(filename)

    apply_filter_on_image(filename, filename)
    
    # process the screenshot
    item_img = Image.open(filename)
    text = pytesseract.image_to_string(item_img)
    try:
        item_current_price = int(''.join(filter(str.isdigit, text)))
    except:
        item_current_price = 1
    
    # Delete the screenshot
    # os.remove(filename)
    ##############

    print(f"Price found ! 1 x {item_name} for {item_current_price} Kamas")

    return {'price': item_current_price}

def parse_recipe_from_json(json_data: list, item_name: str) -> list:
    """
    purpose:
        Parse the JSON data to retrieve the name and level of the specified item's recipe ingredients
    input:
        json_data (list): The JSON data containing item information
        item_name (str) : The name of the item to search for
    output:
        list: List of dictionaries containing the name, quantity, and level of the recipe ingredients
    """

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

def create_report(target: str, parsed_recipe: list) -> None:
    """
    purpose:
        Create a report containing the recipe details for the target item
    input:
        target (str)        : The name of the target item
        parsed_recipe (list): List of dictionaries containing the recipe details
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
    with open("equipment_recipes.json", "r", encoding="utf-8") as file:
        data = json.load(file)

    for target in target_lst:
        parsed_recipe = parse_recipe_from_json(data, target)
        if not parsed_recipe:
            sys.exit("No recipe found. Exiting...")
        
        for resource in parsed_recipe:
            item_name = resource['name']
            item_quantity = resource['quantity']
            item_type = resource['type']
            item_lvl = resource['level']

            price_info = ocr_determine_price(item_name, item_quantity, item_type, item_lvl)
            resource.update(price_info)

        # Create table report for the item
        create_report(target, parsed_recipe)

    ending_message()

if __name__ == "__main__":  
    main()