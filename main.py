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

mouse = pynput.mouse.Controller()
keyboard = pynput.keyboard.Controller()
pytesseract.pytesseract.tesseract_cmd = r'C:\\Users\\richa\AppData\\Local\\Programs\\Tesseract-OCR\\tesseract.exe'

# Click function 
def do_click(nb: int, x: int, y: int):
    delay = round(uniform(0,1), 2)
    sleep(delay) # between 2 and 3 s

    for _ in range(nb):
        mouse.position = (x, y)
        delay = round(uniform(100,300), 2)/1000000.0
        sleep(delay) # between 100 and 300 ms
        mouse.press(pybtn.left)
        mouse.release(pybtn.left)

def get_resource_price(prices_dct : dict):
    items_lst = prices_dct.keys()
    
    # 2000, 640 open HDV
    # do_click(1, 2000, 640) 
    # sleep(5) # wait hdv in charging   

    now = datetime.now()
    now = now.strftime("%Y%m%d%H%M%S")

    for item in items_lst:

        # clear research
        do_click(1, 462, 162) 
        sleep(0.2)

        # click on searchbar
        do_click(1, 350, 166) 
        sleep(0.2) 

        # write the name of the item in searchbar
        keyboard.type(item)
        sleep(0.7) 

        # select item to diplay the price
        do_click(1, 610, 184) 
        sleep(1)

        # take screenshot of average price (N K/u)       
        im=ImageGrab.grab(bbox=(920,260,1025,290))
        filename = f"{item}-{now}.png" 
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

        prices_dct[item] = item_current_price

        print(f"Price found ! 1 x {item} for {item_current_price} Kamas")    

def calculate_raw_cost(recipe_dct : dict, prices_dct : dict):
    # calculating raw materials cost
    raw_cost = 0
    for item in recipe_dct.keys():
        item_cost = recipe_dct[item] * prices_dct[item]
        raw_cost += item_cost
    return raw_cost

def main():

    target = create_window()
    table = PrettyTable()
    table.field_names = ["Item", "Raw cost + taxes"]
    table.align['Item'] = "l"
    table.align['Raw cost + taxes'] = "l"

    with open("recipe.json", "r", encoding="utf-8") as file:
        data = json.load(file)

    for item in data:
        if item['name'] in target:
            prices_dct = dict()
            recipe_dct = dict()

            selling_item_name = item['name']
            recipe_lst = item['recipe']        

            for item_dct in recipe_lst:
                name = item_dct['name']
                quantity = item_dct['quantity']

                recipe_dct[name] = quantity
                prices_dct[name] = None

            get_resource_price(prices_dct)

            # calculating raw materials cost    
            raw_cost = calculate_raw_cost(recipe_dct, prices_dct)
            taxes = 0.02 * raw_cost

            net_cost = raw_cost + taxes
            table.add_row([f"{selling_item_name}", f"{net_cost:.0f} kamas"])               
    
    ending_message()
    print(table)

if __name__ == "__main__":  
    main()