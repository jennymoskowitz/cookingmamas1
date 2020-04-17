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

        for x in range(len(data['recipes'])):
            if len(data['recipes'][x]['cuisines']) > 0:
                if data['recipes'][x]['cuisines'][0] not in dict1:
                    dict1[data['recipes'][x]['cuisines'][0]] = 0
                dict1[data['recipes'][x]['cuisines'][0]] += 1
            else:
                print("Cuisine not found.")

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

        return cuisine_ingredients

    def get_tasty_database(self, cuisine, cur, conn):
        r = self.get_tasty_recipes(cuisine)
        data = json.loads(r.text)
        cur.execute(''' SELECT count(name) FROM sqlite_master WHERE type='table' AND name='Tasty' ''')
        if cur.fetchone()[0]==1:
            for x in range(len(data['results'])):
                recipe_id = data['results'][x]["id"]
                try:
                    name = data["results"][x]["name"]
                except:
                    name = data["results"][x]["seo_title"]
                if "_" in cuisine:
                    join_word = []
                    split_cuisine = cuisine.split("_")
                    for word in split_cuisine:
                        w = word[0].upper() + word[1:]
                        join_word.append(w)
                    c = (" ").join(join_word)
                else:
                    c = cuisine[0].upper() + cuisine[1:]
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
                cur.execute('''INSERT OR REPLACE INTO Tasty (recipe_id, name, cuisine, ingredients) VALUES (?, ?, ?, ?)''', (recipe_id, name, c, str(ingredients)))
            conn.commit()
        else:
            cur.execute('''CREATE TABLE Tasty (recipe_id TEXT PRIMARY KEY, name TEXT, cuisine TEXT, ingredients TEXT)''')
            for x in range(len(data['results'])):
                recipe_id = data['results'][x]["id"]
                try:
                    name = data["results"][x]["name"]
                except:
                    name = data["results"][x]["seo_title"]
                if "_" in cuisine:
                    join_word = []
                    split_cuisine = cuisine.split("_")
                    for word in split_cuisine:
                        w = word[0].upper() + word[1:]
                        join_word.append(w)
                    c = (" ").join(join_word)
                else:
                    c = cuisine[0].upper() + cuisine[1:]
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
                cur.execute('''INSERT OR REPLACE INTO Tasty (recipe_id, name, cuisine, ingredients) VALUES (?, ?, ?, ?)''', (recipe_id, name, c, str(ingredients)))
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
                cur.execute('''INSERT OR REPLACE INTO Spoonacular (recipe_id, name, cuisine, ingredients) VALUES (?, ?, ?, ?)''', (recipe_id, name, cuisine, str(ingredients)))
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
                cur.execute('''INSERT OR REPLACE INTO Spoonacular (recipe_id, name, cuisine, ingredients) VALUES (?, ?, ?, ?)''', (recipe_id, name, cuisine, str(ingredients)))
            conn.commit()
    
    def get_ingredients_lst(self, cuisine):
            ingredients = self.get_ingredients(cuisine)
            ingredients_dict= {}
            for x in ingredients:
                for y in x: 
                    if y in ingredients_dict: 
                        ingredients_dict[y] += 1
                    else: 
                        ingredients_dict[y] = 0 
                        ingredients_dict[y] += 1
            sorted_dict = sorted(ingredients_dict, reverse=True)
            sorted_keys = sorted_dict.keys()
            i1 = sorted_keys[0]
            i2 = sorted_keys[1]
            i3 = sorted_keys[2]
            i4 = sorted_keys[3]
            i5 = sorted_keys[4]
#this is the one from above- spoonacular bar graph of cusines and # of recipes
#def cuisine_visualization(self):
#         r = Tasty()
#         dict1 = r.get_dict()
#         fig = plt.figure(figsize = (10, 5))
#         ax1 = fig.add_subplot(121)
#         ax1.bar([1,2,3], [3,4,5], color='pink')
#         names = dict1.keys()
#         values = dict1.values()
#         plt.bar(names, values)
#         plt.suptitle("Top Cuisines")
#         plt.show()

    #most popular ingredients
    for i in 
 #input: none
    #output: none
    #creates the pie chart breakdown of percent of recipes top 5 ingredients are in 
    def pie_chart(self):
        labels = 'i1', 'i2', 'i3', 'i4', 'i5', 'others'
        #sizes = [self.micro_percent, self.brewpub_percent, self.regional_percent, self.contract_percent, self.planning_percent, self.proprietor_percent, self.large_percent, self.bar_percent]
        explode = (0, 0.1, 0, 0, 0, 0, 0, 0)
        fig1, ax1 = plt.subplots()
        ax1.pie(sizes, explode=explode, shadow=True, startangle=90)
        ax1.axis('equal') 
        #plt.legend( loc = 'best', labels=['%s, %1.1f %%' % (l, s) for l, s in zip(labels, sizes)])
        plt.title("Pie Chart of Most Popular Ingredients")
        plt.show()

    #input: cursor and conncetion to the database to access its data
    #output: none
    #creates the histogram of Average Calories by Cuisine Type
    def priceHistogram(self, cur, conn):
        #Events - Histogram
        numEvents = 0
        prices = cur.execute("SELECT Min_Price, Max_Price FROM Event_Prices")

        averagePrices = []

        for minp, maxp in prices:
            if minp != "n/a" and maxp != "n/a":
                avg = (float(minp) + float(maxp))/2
                averagePrices.append(avg)
            numEvents += 1
        
        #print(averagePrices)
        sortedAveragePrices = sorted(averagePrices)
        #print(sortedAveragePrices)

        plt.xlabel("Cuisine Type")
        plt.ylabel("Average Number of Calories")
        plt.title("Histogram of Average Calories of Recipes by Cusine Type")
        plt.xlim(sortedAveragePrices[0], sortedAveragePrices[-1])
        plt.ylim(0, 15)

        plt.hist(sortedAveragePrices, bins=numEvents, range=None, density=None, weights=None, cumulative=False, bottom=None, histtype='bar', align='mid', orientation='vertical', rwidth=None, log=False, color=None, label=None, stacked=False, normed=None, data=None)

        plt.show()
    
    def generate_scatter(self):
        np.random.seed(19680801)
        N = 50
        srt = sorted(self.combos, key=lambda x: x[1])
        for pair in srt:
            x = pair[0]
            y = pair[1]
            if(pair[1] > 50000):
                continue
            plt.plot(x, y, 'o', c='blue')
            plt.xlabel("Distance in Miles")
            plt.ylabel("Time in Seconds")
        plt.show()
    

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

        querystring = {"app_id": "e29147b2", "app_key": "b34772921762c60de0b5875b765b707a", "ingr": ingredients}

        response = requests.request("GET", url, params=querystring)

        print(response.text)

        return response

    def get_carbs(self, ingredients):
        count = 0
        r = self.get_nutrient_data(ingredients)
        data = json.loads(r.text)
        carb_units = data['totalNutrients']["CHOCDF"]['unit']
        for ingredient in ingredients:
            carb_quantity = data['totalNutrients']["CHOCDF"]['quantity']
            count += carb_quantity
        print(str(count) + carb_units)
        return str(count) + carb_units

    def get_fiber(self, ingredients):
        count = 0
        r = self.get_nutrient_data(ingredients)
        data = json.loads(r.text)
        fiber_units = data['totalNutrients']["FIBTG"]['unit']
        for ingredient in ingredients:
            fiber_quantity = data['totalNutrients']["FIBTG"]['quantity']
            count += fiber_quantity
        print(str(count) + fiber_units)
        return str(count) + fiber_units
    
    def get_calories(self, ingredients):
        count = 0
        r = self.get_nutrient_data(ingredients)
        data = json.loads(r.text)
        for ingredient in ingredients:
            calories = data['calories']
            count += calories
        print(str(count))
        return str(count)



g = Edamam()
#g.get_carbs(["1 fresh ham", "7 cloves garlic, minced"])
#g.get_fiber(['1 teaspoon garlic powder', '1 teaspoon salt', '1 ½ cups crema table cream', '24 soft corn tortillas', 'Oil for frying', 'Crema', 'Cilantro', 'Cotija cheese', 'Avocado'])
# g.get_calories(["1 fresh ham, about 18 pounds, prepared by your butcher (See Step 1)",
#     "7 cloves garlic, minced",
#     "1 tablespoon caraway seeds, crushed",
#     "4 teaspoons salt",
#     "Freshly ground pepper to taste",
#     "1 teaspoon olive oil",
#     "1 medium onion, peeled and chopped",
#     "3 cups sourdough rye bread, cut into 1/2-inch cubes",
#     "1 1/4 cups coarsely chopped pitted prunes",
#     "1 1/4 cups coarsely chopped dried apricots",
#     "1 large tart apple, peeled, cored and cut into 1/2-inch cubes",
#     "2 teaspoons chopped fresh rosemary",
#     "1 egg, lightly beaten",
#     "1 cup chicken broth, homemade or low-sodium canned"])


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
        # change the format to put in the next api
        # if the cuisine has two words
        if ' ' in rec:
            # split the two names and make the first letter of each lower case and then join
            # them with a _
            name_list = []
            split_name = rec.split(" ")
            for word in split_name:
                name = word[0].lower() + word[1:]
                name_list.append(name)
                r = ('_').join(name_list)
        else:
            # make the first letter lower case in the cuisine in order to input it into the next api
            r = rec[0].lower() + rec[1:]
        # input the cuisine into the tasty api and output a list of ingredients for each recipie for the cuisine
        tasty = v.get_ingredients(r)
        #set up or accumulate to the tasty table
        v.get_tasty_database(r, cur, conn)

    recipe = Edamam()
    for ingredients in tasty:
        recipe.get_carbs(ingredients)
        recipe.get_fiber(ingredients)
        recipe.get_calories(ingredients)

if __name__ == "__main__":
    main()