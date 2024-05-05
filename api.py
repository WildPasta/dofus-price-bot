##########
# Author: wildpasta
# Description: query module for DofusDB API
##########

# Python standard libraries
import sys

# Third-party libraries
import requests
from urllib.parse import quote

def get_user_input() -> tuple:
    """ 
    purpose: 
        Get the item name and level from the user
    input:  
        None
    output:
        url_enc_item_name, item_lvl (tuple): tuple containing the URL encoded item name and the item level
    """

    try:
        item_name = input("Enter the name of the item: ")
        url_enc_item_name = quote(item_name)
        item_lvl = int(input("Enter the level of the item: "))

        return url_enc_item_name, item_lvl

    except ValueError:
        exit("Invalid input. Exiting...")
    except Exception as e:
        exit(f"An error occured with input parsing: {e}. Exiting...")

def send_api_request(url: str, headers: dict) -> dict:
    """ 
    purpose: 
        Send a GET request to the DofusDB API
    input:  
        url (str): URL to send the request to
        headers (dict): HTTP headers to include in the request
    output:
        dict: JSON response from the API
    """

    response = requests.get(url, headers=headers)

    try:
        if response.status_code == 200:
            data = response.json()
            
            # When requesting an item based on name, the API returns a 'total' key with a value of 0 if it doesn't exist
            if 'total' in data and data['total'] == 0:
                raise ValueError("No item found with the given name and level.")
            
            return data

        else:
            raise ValueError(f"Request failed (Status code: {response.status_code})")
    
    except ValueError as e:
        exit(f"Error: {e} Exiting...")
    except Exception as e:
        exit(f"Error: {e} Exiting...")

def find_item_id(headers: dict, item_name: str, item_lvl: int) -> int:
    """ 
    purpose: 
        Find the ID of an item based on its name and level
    input:  
        headers (dict): HTTP headers to include in the request
        item_name (str): Name of the item to search for
        item_lvl (int): Level of the item to search for
    output:
        int: The ID of the found item
    """

    url = f"https://api.dofusdb.fr/items?slug.fr[$search]={item_name}&level[$gte]={item_lvl}&level[$lte]={item_lvl}&"
    response = send_api_request(url, headers)

    try:
        item_id = response['data'][0]['id']
        return item_id

    except Exception as e:
        exit(f"Error: {e} Exiting...")

def retrieve_ingredients(headers: dict, item_id: int) -> list:
    """ 
    purpose: 
        Retrieve the ingredients of a recipe based on the item ID.
    input:  
        headers (dict): HTTP headers to include in the request
        item_id (int): ID of the item to retrieve ingredients for
    output:
        list: List of dictionaries containing details of the ingredients
    """

    url = f"https://api.dofusdb.fr/recipes/{item_id}?$select[]=ingredientIds&$select[]=quantities&lang=fr"
    response = send_api_request(url, headers)
    ingredient_list = list()

    try:
        # Construction of the dictionary with id/quantity pairs
        ingredient_dict = dict(zip(response['ingredientIds'], response['quantities']))
        
        # Some item ids are not in ascending order, so we must sort them
        sorted_ingredient_dict = dict(sorted(ingredient_dict.items()))

        # We retrieve the names of the ingredients
        for i in range(len(sorted_ingredient_dict)):
            ingredient_id = response['ingredients'][i]['id']
            ingredient_name = response['ingredients'][i]['name']['fr']
            ingredient_level = response['ingredients'][i]['level']
            ingredient_dict = {
                'name': ingredient_name,
                'quantity': sorted_ingredient_dict[ingredient_id],
                'level': ingredient_level
            }
            ingredient_list.append(ingredient_dict)

        return ingredient_list

    except Exception as e:
        exit(f"Error: {e} Exiting...")

def main() -> None:
    """
    purpose:
        Main function
    input:
        None
    output:
        None
    """

    # Get the item name and level from the user
    item_name, item_lvl = get_user_input()

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36'
    }

    # Retrieve the item id
    item_id = find_item_id(headers, item_name, item_lvl)

    # Retrieve the ingredients as json
    ingredients = retrieve_ingredients(headers, item_id)
    
    if ingredients != None:
        print(ingredients)

if __name__ == "__main__":
    sys.exit(main())
