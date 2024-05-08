import os
import pynput
import pytesseract
from datetime import datetime
from gui import *
from PIL import Image
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

def do_click(nb: int, x: int, y: int):
    delay = round(uniform(0,1), 2)
    sleep(delay) # between 2 and 3 s

    for _ in range(nb):
        mouse.position = (x, y)
        delay = round(uniform(100,300), 2)/1000000.0
        sleep(delay) # between 100 and 300 ms
        mouse.press(pybtn.left)
        mouse.release(pybtn.left)

def get_resource_price(item_name, item_quantity, item_lvl):
  
    # 2000, 640 open HDV
    # do_click(1, 2000, 640) 
    # sleep(5) # wait hdv is loading   

    now = datetime.now()
    now = now.strftime("%Y%m%d%H%M%S")
    # clear research
    do_click(1, 759, 268) 
    sleep(0.2)

    # click on searchbar
    do_click(1, 555, 264) 
    sleep(0.2) 

    # write the name of the item in searchbar
    keyboard.type(item_name)
    sleep(0.7) 

    # select item to diplay the price
    do_click(1, 856, 305) 
    sleep(1)

    # take screenshot of average price (N K/u)    
    # x_top_left, y_top_left, x_bottom_right, y_bottom_right   
    im=ImageGrab.grab(bbox=(1226, 330, 1380, 400))

    filename = f"{item_name}-{now}.png" 
    im.save(filename)

    # analyze the price
    item_img = Image.open(filename)
    text = pytesseract.image_to_string(item_img)
    try:
        item_current_price = int(''.join(filter(str.isdigit, text)))
    except:         
        item_current_price = 1

    # Delete the screenshot 
    os.remove(filename)

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

def ocr_resource_price(item_name: str, item_quantity: int, item_lvl: int):
    # print(f"Name: {item_name}")
    # print(f"Quantity: {item_quantity}")
    # print(f"Level: {item_lvl}")

    price_found = 33
    return {'price': price_found}

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

    target_lst = ["Ceinture du Piou Bleu"]
    for target in target_lst:
        parsed_recipe = parse_recipe_from_json(data, target)
        if not parsed_recipe:
            sys.exit("No recipe found. Exiting...")
        
        for resource in parsed_recipe:
            item_name = resource['name']
            item_quantity = resource['quantity']
            item_lvl = resource['level']

            # price_info = ocr_resource_price(item_name, item_quantity, item_lvl)
            price_info = get_resource_price(item_name, item_quantity, item_lvl)
            resource.update(price_info)

        # Create table report for the item
        create_report(target, parsed_recipe)

    ending_message()

if __name__ == "__main__":  
    main()