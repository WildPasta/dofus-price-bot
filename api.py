import requests
import sys

def find_id_from_inputs(headers, item_name, item_lvl):
    url = f"https://api.dofusdb.fr/items?slug.fr[$search]={item_name}&level[$gte]={item_lvl}&level[$lte]={item_lvl}&"

    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        item_id = response.json()['data'][0]['id']
        return item_id
    else:   
        print(f"Objet non trouvé (Retour {response.status_code})")

def retrieve_ingredients(headers, item_id):
    url = f"https://api.dofusdb.fr/recipes/{item_id}?$select[]=ingredientIds&$select[]=quantities&lang=fr"
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        data = response.json()
        ingredient_list = list()

        # Construction du dictionnaire avec les couples id/quantité
        ingredient_dict = dict(zip(data['ingredientIds'], data['quantities']))
        
        # Tri du dictionnaire dans l'ordre croissant des ids
        # Certains id d'item ne sont pas dans l'ordre croissant et dans le retour de l'api ils le sont donc ont doit classer
        sorted_ingredient_dict = dict(sorted(ingredient_dict.items()))

        # On récupère le nom des ingrédients
        for i in range(len(sorted_ingredient_dict)):
            ingredient_id = data['ingredients'][i]['id']
            ingredient_name = data['ingredients'][i]['name']['fr']
            ingredient_level = data['ingredients'][i]['level']
            ingredient_dict = {
                'name': ingredient_name,
                'quantity': sorted_ingredient_dict[ingredient_id],
                'level': ingredient_level
            }
            ingredient_list.append(ingredient_dict)
        
        # Retourne une liste de dictionnaire avec les ingrédients
        return ingredient_list
    else:
        print(f"Recette non trouvée (Retour {response.status_code})")

def main():
    item_name_input = str(input("Entrez le nom de l'item : "))
    item_lvl_input = str(input("Entrez le niveau de l'item : "))

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36'
    }

    item_id = find_id_from_inputs(headers, item_name_input, item_lvl_input)

    ingredients = retrieve_ingredients(headers, item_id)
    
    if ingredients != None:
        print(ingredients)

if __name__ == "__main__":
    sys.exit(main())