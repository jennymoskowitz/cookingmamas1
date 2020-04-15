import requests
import json
import sqlite3
import matplotlib
import matplotlib.pyplot as plt
import math
import numpy as np
import os
import random


#dir_path = os.path.dirname(os.path.realpath(__file__))
#self.CACHE_FNAME = dir_path + '/' + "cache_spoonacular.json"

def read_cache(CACHE_FNAME):
    """
    This function reads from the JSON cache file and returns a dictionary from the cache data.
    If the file doesn't exist, it returns an empty dictionary.
    """
    try:
        cache_file = open(CACHE_FNAME, 'r', encoding="utf-8") # Try to read the data from the file
        cache_contents = cache_file.read()  # If it's there, get it into a string
        CACHE_DICTION = json.loads(cache_contents) # And then load it into a dictionary
        cache_file.close() # Close the file, we're good, we got the data in a dictionary.
        return CACHE_DICTION
    except:
        CACHE_DICTION = {}
        return CACHE_DICTION

def write_cache(CACHE_FNAME, CACHE_DICT):
    """
    This function encodes the cache dictionary (CACHE_DICT) into JSON format and
    writes the JSON to the cache file (CACHE_FNAME) to save the search results.
    """
    with open(CACHE_FNAME, 'w') as f:
        json.dump(CACHE_DICT, f)


#Spoonacular 
#get recipies
class Spoonacular:

    def get_recipies(self):
        url = 'https://api.spoonacular.com/recipes/random'
        params = {"apiKey" : '3adec4cbad224f2c9596d4c011d346fc', "number" : "1"}
        response = requests.request("GET", url, params = params)
        print(response.text)
        #data = json.loads(r.text)
        return response

    def get_dict(self):
        dict1 = {}
        r = self.get_recipies()
        data = json.loads(r.text)
        print(data)
        for x in range(len(data['recipes'])):
            try:
                if len(data['recipes'][x]['cuisines']) > 0:
                    if data['recipes'][x]['cuisines'][0] not in dict1:
                        dict1[data['recipes'][x]['cuisines'][0]] = 0
                    dict1[data['recipes'][x]['cuisines'][0]] += 1
                else:
                    print("Cuisine not found.")


                    


    #   




class Tasty:
    def get_tasty_recipes(self):
        url = "https://tasty.p.rapidapi.com/recipes/list"
        x = random.randrange(0, 40)
        y = random.randrange(50, 300)
        querystring = {"from": x,"sizes": y}

        headers = {'x-rapidapi-host': "tasty.p.rapidapi.com",'x-rapidapi-key': "74c1de20bdmsh109b356a35082c3p1cf14cjsn37f52eca5a61"}

        response = requests.request("GET", url, headers=headers, params=querystring)
        return response

    def get_list(self):
        list1 = []
        for x in range(5):
            var = self.get_tasty_recipes()
            list1.append(var)
        return list1

    def get_dict(self):
        dict1 = {}
        list1 = self.get_list()
        for var in list1:
            data = json.loads(var.text)
            for val in range(len(data['results'])):
                try:
                    for tag in data['results'][val]["tags"]:
                        if tag['type'] == 'cuisine': 
                            x = tag['display_name']
                            if x not in dict1:
                                dict1[x] = 0
                            dict1[x] += 1
                        #     break
                        # else:
                        #     if tag['type'] == 'dietary':
                        #         x = tag['display_name']
                        #         if x not in dict1:
                        #             dict1[x] = 0
                        #         dict1[x] += 1 
                except:
                    x = "Cuisine not classified"     
                    if x not in dict1:
                        dict1[x] = 0
                    dict1[x] += 1   
        print(dict1)
        return dict1

    def setUpDatabase(self):
        path = os.path.dirname(os.path.abspath(__file__))
        self.conn = sqlite3.connect(path+'/'+'Cookingmamas.db')
        self.cur = self.conn.cursor()
        return self.cur, self.conn
    
    def get_tasty_database(self):
        list1 = self.get_list()
        self.cur.execute("DROP TABLE IF EXISTS Tasty")
        self.cur.execute('''CREATE TABLE Tasty (recipe_id TEXT PRIMARY KEY, name TEXT, cuisine TEXT, ingregients TEXT,)''')
        for var in list1:
            data = json.loads(var.text)
            for x in range(len(data['results'])):
                recipe_id = data['results'][x]["id"]
                name = data["results"][x]["seo_title"]
                for tag in data['results'][x]["tags"]:
                    if tag['type'] == 'cuisine': 
                        cuisine = tag['display_name']
                        break
                    elif tag['type'] == 'dietary':
                        cuisine = tag['display_name']
                    else:
                        cuisine = "Cuisine not classified"
                ingredients = []
                for component in data['results'][x]["section"]:
                    ingredients.append(component['name'])
                self.cur.execute('''INSERT INTO Tasty (recipe_id, name, cuisine, ingredients) VALUES (?, ?, ?, ?)''', (recipe_id, name, cuisine, str(ingredients)))
        self.conn.commit()



    def visualization(self):
        r = Tasty()
        dict1 = r.get_dict()
        fig = plt.figure(figsize = (10, 5))
        ax1 = fig.add_subplot(121)
        ax1.bar([1,2,3], [3,4,5])
        names = dict1.keys()
        values = dict1.values()
        plt.bar(names, values)
        plt.suptitle("Top Cuisines")
        plt.show()




var = Tasty()
var.get_dict()
