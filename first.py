import requests
from bs4 import BeautifulSoup
import json
import sqlite3
import matplotlib
import matplotlib.pyplot as plt
import math
import numpy as np
import os
import random
import re





#dir_path = os.path.dirname(os.path.realpath(__file__))
#self.CACHE_FNAME = dir_path + '/' + "cache_spoonacular.json"

# def read_cache(CACHE_FNAME):
#     """
#     This function reads from the JSON cache file and returns a dictionary from the cache data.
#     If the file doesn't exist, it returns an empty dictionary.
#     """
#     try:
#         cache_file = open(CACHE_FNAME, 'r', encoding="utf-8") # Try to read the data from the file
#         cache_contents = cache_file.read()  # If it's there, get it into a string
#         CACHE_DICTION = json.loads(cache_contents) # And then load it into a dictionary
#         cache_file.close() # Close the file, we're good, we got the data in a dictionary.
#         return CACHE_DICTION
#     except:
#         CACHE_DICTION = {}
#         return CACHE_DICTION

# def write_cache(CACHE_FNAME, CACHE_DICT):
#     """
#     This function encodes the cache dictionary (CACHE_DICT) into JSON format and
#     writes the JSON to the cache file (CACHE_FNAME) to save the search results.
#     """
#     with open(CACHE_FNAME, 'w') as f:
#         json.dump(CACHE_DICT, f)


class Recipies:

    def set_up_recipie_database(self, db_name):
        path = os.path.dirname(os.path.abspath(__file__))
        conn = sqlite3.connect(path+'/'+db_name)
        cur = conn.cursor()
        return cur, conn

    def get_recipies(self):
        url = 'https://api.spoonacular.com/recipes/random'
        params = {"apiKey" : '3adec4cbad224f2c9596d4c011d346fc', "number" : "100"}
        response = requests.request("GET", url, params = params)

        return response

    def get_dict(self):
        dict1 = {}
        r = self.get_recipies()
        data = json.loads(r.text)
        print(data)
        for x in range(len(data['recipes'])):
            if len(data['recipes'][x]['cuisines']) > 0:
                if data['recipes'][x]['cuisines'][0] not in dict1:
                    dict1[data['recipes'][x]['cuisines'][0]] = 0
                dict1[data['recipes'][x]['cuisines'][0]] += 1
            else:
                print("Cuisine not found.")
        print(dict1)
        # sorted_dict = sorted(dict1.items(), key = lambda t: t[1], reverse = True)
        # l = []
        # for tup in sorted_dict:
        #     l.append(tup[0])
        # print(l)
        return dict1.keys()
    
    def get_tasty_recipes(self, cuisine):
        url = "https://tasty.p.rapidapi.com/recipes/list"
 
        querystring = {"tags": cuisine, "from": 0,"sizes": 20}

        headers = {'x-rapidapi-host': "tasty.p.rapidapi.com",'x-rapidapi-key': "74c1de20bdmsh109b356a35082c3p1cf14cjsn37f52eca5a61"}

        response = requests.request("GET", url, headers=headers, params=querystring)

        return response


    def get_ingredients(self, cuisine):
        cuisine_ingredients = []
        r = self.get_tasty_recipes(cuisine)
        data = json.loads(r.text)
        for x in range(len(data['results'])):
            ingredients = []
            try:
                for num in range(len(data['results'][x]['sections'])):
                    for n in range(len(data['results'][x]['sections'][num]['components'])):
                        ingredients.append(data['results'][x]['sections'][num]['components'][n]['raw_text'])
            except:
                for num in range(len(data['results'][x]["recipes"])):
                    for n in range(len(data['results'][x]["recipes"][num]['sections'])):
                        for j in range(len(data['results'][x]["recipes"][num]['sections'][n]['components'])):
                            ingredients.append(data['results'][x]["recipes"][num]['sections'][n]['components'][j]['raw_text'])
            cuisine_ingredients.append(ingredients)
        print(cuisine_ingredients)
        return cuisine_ingredients

    def get_tasty_database(self, cuisine, cur, conn):
        r = self.get_tasty_recipes(cuisine)
        data = json.loads(r.text)
        cur.execute(''' SELECT count(name) FROM sqlite_master WHERE type='table' AND name='Tasty' ''')
        if cur.fetchone()[0]==1:
            for x in range(len(data['results'])):
                recipe_id = data['results'][x]["id"]
                name = data["results"][x]["seo_title"]
                c = cuisine
                # for tag in data['results'][x]["tags"]:
                #     if tag['type'] == 'cuisine': 
                #         cuisine = tag['display_name']
                #         break
                #     else:
                #         cuisine = "Cuisine not classified"
                ingredients = []
                try:
                    for num in range(len(data['results'][x]['sections'])):
                        for n in range(len(data['results'][x]['sections'][num]['components'])):
                            ingredients.append(data['results'][x]['sections'][num]['components'][n]['raw_text'])
                except:
                    for num in range(len(data['results'][x]["recipes"])):
                        for n in range(len(data['results'][x]["recipes"][num]['sections'])):
                            for j in range(len(data['results'][x]["recipes"][num]['sections'][n]['components'])):
                                ingredients.append(data['results'][x]["recipes"][num]['sections'][n]['components'][j]['raw_text'])
                cur.execute('''INSERT INTO Tasty (recipe_id, name, cuisine, ingredients) VALUES (?, ?, ?, ?)''', (recipe_id, name, c, str(ingredients)))
            conn.commit()
        else:
            cur.execute('''CREATE TABLE Tasty (recipe_id TEXT PRIMARY KEY, name TEXT, cuisine TEXT, ingredients TEXT)''')
            for x in range(len(data['results'])):
                recipe_id = data['results'][x]["id"]
                name = data["results"][x]["seo_title"]
                c = cuisine
                # for tag in data['results'][x]["tags"]:
                #     if tag['type'] == 'cuisine': 
                #         cuisine = tag['display_name']
                #         break
                #     else:
                #         cuisine = "Cuisine not classified"
                ingredients = []
                try:
                    for num in range(len(data['results'][x]['sections'])):
                        for n in range(len(data['results'][x]['sections'][num]['components'])):
                            ingredients.append(data['results'][x]['sections'][num]['components'][n]['raw_text'])
                except:
                    for num in range(len(data['results'][x]["recipes"])):
                        for n in range(len(data['results'][x]["recipes"][num]['sections'])):
                            for j in range(len(data['results'][x]["recipes"][num]['sections'][n]['components'])):
                                ingredients.append(data['results'][x]["recipes"][num]['sections'][n]['components'][j]['raw_text'])
                cur.execute('''INSERT INTO Tasty (recipe_id, name, cuisine, ingredients) VALUES (?, ?, ?, ?)''', (recipe_id, name, c, str(ingredients)))
            conn.commit()
    

    def get_spoon_database(self, cur, conn):
        r = self.get_recipies()
        data = json.loads(r.text)
        cur.execute(''' SELECT count(name) FROM sqlite_master WHERE type='table' AND name='Spoonacular' ''')
        if cur.fetchone()[0]==1:
            for x in range(len(data['recipes'])):
                recipe_id = data['recipes'][x]["id"]
                name = data['recipes'][x]['title']
                if len(data['recipes'][x]['cuisines']) > 0:
                    cuisine = data['recipes'][x]['cuisines'][0]
            
                else:
                    cuisine = "Cuisine not classified"
                ingredients = []
                for num in range(len(data['recipes'][x]['analyzedInstructions'])):
                    for n in range(len(data['recipes'][x]['analyzedInstructions'][num]['steps'])):
                        for j in range(len(data['recipes'][x]['analyzedInstructions'][num]['steps'][n]['ingredients'])):
                            ingredients.append(data['recipes'][x]['analyzedInstructions'][num]['steps'][n]['ingredients'][j]['name'])
                cur.execute('''INSERT INTO Spoonacular (recipe_id, name, cuisine, ingredients) VALUES (?, ?, ?, ?)''', (recipe_id, name, cuisine, str(ingredients)))
            conn.commit()
        else:
            cur.execute('''CREATE TABLE Spoonacular (recipe_id TEXT PRIMARY KEY, name TEXT, cuisine TEXT, ingredients TEXT)''')
            for x in range(len(data['recipes'])):
                recipe_id = data['recipes'][x]["id"]
                name = data['recipes'][x]['title']
                if len(data['recipes'][x]['cuisines']) > 0:
                    cuisine = data['recipes'][x]['cuisines'][0]
            
                else:
                    cuisine = "Cuisine not classified"
            ingredients = []
            for num in range(len(data['recipes'][x]['analyzedInstructions'])):
                for n in range(len(data['recipes'][x]['analyzedInstructions'][num]['steps'])):
                    for j in range(len(data['recipes'][x]['analyzedInstructions'][num]['steps'][n]['ingredients'])):
                        ingredients.append(data['recipes'][x]['analyzedInstructions'][num]['steps'][n]['ingredients'][j]['name'])
                cur.execute('''INSERT INTO Spoonacular (recipe_id, name, cuisine, ingredients) VALUES (?, ?, ?, ?)''', (recipe_id, name, cuisine, str(ingredients)))
            conn.commit()
    

# v = Recipies()
# cuisines = v.get_dict()
# for rec in cuisines:
#     r = rec[0].lower() + rec[1:]
#     tasty = v.get_ingredients(r)




# class Tasty:
#     # cuisines from spoonacular 
#     def get_tasty_recipes(self, cuisine):
#         url = "https://tasty.p.rapidapi.com/recipes/list"
#         # x = random.randrange(0, 40)
#         # y = random.randrange(50, 300)
 

#         querystring = {"tags": cuisine, "from": 0,"sizes": 20}

#         headers = {'x-rapidapi-host': "tasty.p.rapidapi.com",'x-rapidapi-key': "74c1de20bdmsh109b356a35082c3p1cf14cjsn37f52eca5a61"}

#         response = requests.request("GET", url, headers=headers, params=querystring)
#         return response


#     # def get_list(self):
#     #     list1 = []
#     #     for x in range(5):
#     #         var = self.get_tasty_recipes()
#     #         list1.append(var)
#     #     return list1

#     def get_dict(self):
#         dict1 = {}
#         list1 = self.get_list()
#         for var in list1:
#             data = json.loads(var.text)
#             for val in range(len(data['results'])):
#                 try:
#                     for tag in data['results'][val]["tags"]:
#                         if tag['type'] == 'cuisine': 
#                             x = tag['display_name']
#                             if x not in dict1:
#                                 dict1[x] = 0
#                             dict1[x] += 1
#                         #     break
#                         # else:
#                         #     if tag['type'] == 'dietary':
#                         #         x = tag['display_name']
#                         #         if x not in dict1:
#                         #             dict1[x] = 0
#                         #         dict1[x] += 1 
#                 except:
#                     x = "Cuisine not classified"     
#                     if x not in dict1:
#                         dict1[x] = 0
#                     dict1[x] += 1   
#         print(dict1)
#         return dict1

#     def set_up_database(self, db_name):
#         path = os.path.dirname(os.path.abspath(__file__))
#         conn = sqlite3.connect(path+'/'+db_name)
#         cur = conn.cursor()
#         return cur, conn
    
    # def get_tasty_database(self, cur, conn):
    #     list1 = self.get_list()
    #     cur.execute("DROP TABLE IF EXISTS Tasty")
    #     cur.execute('''CREATE TABLE Tasty (recipe_id TEXT PRIMARY KEY, name TEXT, cuisine TEXT, ingregients TEXT,)''')
    #     for var in list1:
    #         data = json.loads(var.text)
    #         for x in range(len(data['results'])):
    #             recipe_id = data['results'][x]["id"]
    #             name = data["results"][x]["seo_title"]
    #             for tag in data['results'][x]["tags"]:
    #                 if tag['type'] == 'cuisine': 
    #                     cuisine = tag['display_name']
    #                     break
    #                 elif tag['type'] == 'dietary':
    #                     cuisine = tag['display_name']
    #                 else:
    #                     cuisine = "Cuisine not classified"
    #             ingredients = []
    #             for component in data['results'][x]["section"]:
    #                 ingredients.append(component['name'])
    #             cur.execute('''INSERT INTO Tasty (recipe_id, name, cuisine, ingredients) VALUES (?, ?, ?, ?)''', (recipe_id, name, cuisine, str(ingredients)))
    #     conn.commit()



#     def visualization(self):
#         r = Tasty()
#         dict1 = r.get_dict()
#         fig = plt.figure(figsize = (10, 5))
#         ax1 = fig.add_subplot(121)
#         ax1.bar([1,2,3], [3,4,5])
#         names = dict1.keys()
#         values = dict1.values()
#         plt.bar(names, values)
#         plt.suptitle("Top Cuisines")
#         plt.show()


# n = Tasty()
# try:
#     path = os.path.dirname(os.path.abspath(__file__))
#     f = open(path + "/Cookingmamas.db")
#     conn = sqlite3.connect(f)
#     cur = conn.cursor()
# except:
#     cur, conn = n.set_up_database("Cookingmamas.db")


# n.get_tasty_database(cur, conn)

class weight:
    def __init__(self, value, unit = "g"):
        """
        This method is initialized when the object is created
        """
        self.value = value
        self.unit = unit
        # The value of kg is 0.001 (1E-3) because your logic multiplies the input value. So mg must be 1/1E-3 = 1000
        self._metric = {"g" : 1,
                    "kg" : 0.001,
                    "mg" : 1000
                   }

    def convert_to_gram(self):
        """
        This method converts a self.value to g, kg or mg based on self.unit
        """
        return self.value * self._metric[self.unit]

    def __add__(self, other):
        """
        The __add__ method is a 'magic' (dunder) method which gets called when we add two numbers using the + operator.
        this method calls convert_to_gram() methods from this class object and from 'other' class object as well
        it then returns the sum of both convertion results from the two objects
        """
        x = self.convert_to_gram() + other.convert_to_gram()
        return (x/self._metric[self.unit], self.unit)

class Edamam:
    def get_nutrient_data(self, ingredients):
        url = "https://api.edamam.com/api/nutrition-data"

        querystring = {"app_id": "8b85725d", "app_key": "9e1ffb358e3846f5d71b56ab8b75e4dd", "ingr": ingredients}

        response = requests.request("GET", url, params=querystring)

        print(response.text)

        return response

    def get_carbs(self, ingredients):
        data = self.get_nutrient_data(ingredients)
        dictionary= json.loads(data.text)
        carbs_Quantity = dictionary["totalNutrients"]["CHOCDF"]["quantity"]
        carbs_unit = dictionary["totalNutrients"]["CHOCDF"]["unit"]
        print(str(carbs_Quantity) + carbs_unit)
        return str(carbs_Quantity) + carbs_unit

    def get_fiber(self, ingredients):
        data = self.get_nutrient_data(ingredients)
        dictionary = json.loads(data.text)
        fiber_Quantity = dictionary["totalNutrients"]["FIBTG"]["quantity"]
        fiber_unit = dictionary["totalNutrients"]["FIBTG"]["unit"]
        print(str(fiber_Quantity) + fiber_unit)
        return str(fiber_Quantity) + fiber_unit
       


# g = Edamam()
# g.get_carbs(['1 teaspoon garlic powder', '1 teaspoon salt', '1 ½ cups crema table cream', '24 soft corn tortillas', 'Oil for frying', 'Crema', 'Cilantro', 'Cotija cheese', 'Avocado'])
# g.get_fiber(['1 teaspoon garlic powder', '1 teaspoon salt', '1 ½ cups crema table cream', '24 soft corn tortillas', 'Oil for frying', 'Crema', 'Cilantro', 'Cotija cheese', 'Avocado'])



def main():
    # Recipies object
    v = Recipies()

    #see if Cookingmamas.db exists already, if yes, open and append to it
    #if no, create Cookingmamas.db
    try:
        path = os.path.dirname(os.path.abspath(__file__))
        f = open(path + "/Cookingmamas.db")
        conn = sqlite3.connect(f)
        cur = conn.cursor()
    except:
        cur, conn = v.set_up_recipie_database("Cookingmamas.db")

    # get recipies from spoonacular and then get a dictionary of the different cuisines and the amount of recipies
    # that have each then return a list of the cuisines
    cuisines = v.get_dict()

    #set up or accumulate to the spoonacular table
    v.get_spoon_database(cur, conn)

    # for loop through the different cuisines
    for rec in cuisines:
        # make the first letter lower case in the cuisine in order to input it into the next api
        r = rec[0].lower() + rec[1:]
        # input the cuisine into the tasty api and output a list of ingredients for each recipie for the cuisine
        tasty = v.get_ingredients(r)
        #set up or accumulate to the tasty table
        v.get_tasty_database(r, cur, conn)

