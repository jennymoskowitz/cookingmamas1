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


class Recipies:

    #input: name of database
    #output: returns the cursor and connection to the database
    #set up Event.db
    def set_up_recipie_database(self, db_name):
        path = os.path.dirname(os.path.abspath(__file__))
        conn = sqlite3.connect(path+'/'+db_name)
        cur = conn.cursor()
        return cur, conn

    #input: none
    #output: return the 
    #goes through the Spoonacular API to find 100 random recipies
    def get_recipies(self):
        url = 'https://api.spoonacular.com/recipes/random'
        params = {"apiKey" : '3adec4cbad224f2c9596d4c011d346fc', "number" : "100"}
        response = requests.request("GET", url, params = params)

        return response

    #input: none
    #output: returning the dictionary keys
    #goes through the recipies returned from the Spoonacular API and makes a dictionary of the cuisines found.
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
        return dict1.keys()
    
    #input: type of cuisine
    #output: none
    #goes through the tasty API to return 20 recipes of the given cuisine. 
    def get_tasty_recipes(self, cuisine):
        url = "https://tasty.p.rapidapi.com/recipes/list"
 
        querystring = {"tags": cuisine, "from": 0,"sizes": 20}

        headers = {'x-rapidapi-host': "tasty.p.rapidapi.com",'x-rapidapi-key': "74c1de20bdmsh109b356a35082c3p1cf14cjsn37f52eca5a61"}

        response = requests.request("GET", url, headers=headers, params=querystring)

        return response

    #input: type of cuisine
    #output: none
    #goes through the tasty database given the specified cuisine. Returns a list of the cuisine ingredients.
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


    def setUpCategoriesTable(data, cur, conn):
        cuisine_list = []
        for x in range(len(data['recipes'])):
            if len(data['recipes'][x]['cuisines']) > 0:
                cuisine = data['recipes'][x]['cuisines'][0]
            else:
                cuisine = "Cuisine not classified"
            for c in cuisine_list:
                if cuisine not in cuisine_list:
                    cuisine_list.append(cuisine)

        cur.execute("DROP TABLE IF EXISTS Categories")
        cur.execute("CREATE TABLE Categories (id INTEGER PRIMARY KEY, title TEXT)")
        for i in range(len(category_list)):
            cur.execute("INSERT INTO Categories (id,title) VALUES (?,?)",(i,cuisine_list[i]))
        conn.commit()

    
    #input: type of cuisine, cursor and conncetion to the database to create a table within it
    #output: none
    #sets up the Tasty table within the database, if table exists, then only add to the existing database  

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
                cur.execute('SELECT * FROM Categories')
                category_id = 0
                for row in cur:
                    i = row[0]
                    n = row[1]
                    if n == c:
                        category_id = i
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
                cur.execute('''INSERT OR REPLACE INTO Tasty (recipe_id, name, cuisine, cuisine_id, ingredients) VALUES (?, ?, ?, ?, ?)''', (recipe_id, name, c, cuisine_id, str(ingredients)))
            conn.commit()
        else:
            cur.execute('''CREATE TABLE Tasty (recipe_id TEXT PRIMARY KEY, name TEXT, cuisine TEXT, cuisine_id INTEGER, ingredients TEXT)''')
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
                cur.execute('SELECT * FROM Categories')
                category_id = 0
                for row in cur:
                    i = row[0]
                    n = row[1]
                    if n == c:
                        category_id = i
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
                cur.execute('''INSERT OR REPLACE INTO Tasty (recipe_id, name, cuisine, cuisine_id, ingredients) VALUES (?, ?, ?, ?, ?)''', (recipe_id, name, c, cuisine_id, str(ingredients)))
            conn.commit()
    
    #input: cursor and conncetion to the database to create a table within it
    #output: none
    #sets up the Spoonacular table within the database, if table exists, then only add to the existing database  

    def get_spoon_database(self, cur, conn):
        r = self.get_recipies()
        data = json.loads(r.text)
        cur.execute(''' SELECT count(name) FROM sqlite_master WHERE type='table' AND name='Spoonacular' ''')
        if cur.fetchone()[0]==1:
            for x in range(len(data['recipes'][0:20])):
                recipe_id = data['recipes'][x]["id"]
                name = data['recipes'][x]['title']
                if len(data['recipes'][x]['cuisines']) > 0:
                    cuisine = data['recipes'][x]['cuisines'][0]
            
                else:
                    cuisine = "Cuisine not classified"
                cur.execute('SELECT * FROM Categories')
                category_id = 0
                for row in cur:
                    i = row[0]
                    n = row[1]
                    if n == cuisine:
                        category_id = i
                ingredients = []
                for num in range(len(data['recipes'][x]['analyzedInstructions'])):
                    for n in range(len(data['recipes'][x]['analyzedInstructions'][num]['steps'])):
                        for j in range(len(data['recipes'][x]['analyzedInstructions'][num]['steps'][n]['ingredients'])):
                            ingredients.append(data['recipes'][x]['analyzedInstructions'][num]['steps'][n]['ingredients'][j]['name'])
                cur.execute('''INSERT OR REPLACE INTO Spoonacular (recipe_id, name, cuisine, cuisine_id, ingredients) VALUES (?, ?, ?, ?, ?)''', (recipe_id, name, cuisine, cuisine_id, str(ingredients)))
            conn.commit()
        else:
            cur.execute('''CREATE TABLE Spoonacular (recipe_id TEXT PRIMARY KEY, name TEXT, cuisine TEXT, cuisine_id INTEGER, ingredients TEXT)''')
            for x in range(len(data['recipes'][0:20])):
                recipe_id = data['recipes'][x]["id"]
                name = data['recipes'][x]['title']
                if len(data['recipes'][x]['cuisines']) > 0:
                    cuisine = data['recipes'][x]['cuisines'][0]
            
                else:
                    cuisine = "Cuisine not classified"
                cur.execute('SELECT * FROM Categories')
                category_id = 0
                for row in cur:
                    i = row[0]
                    n = row[1]
                    if n == cuisine:
                        cuisine_id = i
            ingredients = []
            for num in range(len(data['recipes'][x]['analyzedInstructions'])):
                for n in range(len(data['recipes'][x]['analyzedInstructions'][num]['steps'])):
                    for j in range(len(data['recipes'][x]['analyzedInstructions'][num]['steps'][n]['ingredients'])):
                        ingredients.append(data['recipes'][x]['analyzedInstructions'][num]['steps'][n]['ingredients'][j]['name'])
                cur.execute('''INSERT OR REPLACE INTO Spoonacular (recipe_id, name, cuisine, cuisine_id, ingredients) VALUES (?, ?, ?, ?, ?)''', (recipe_id, name, cuisine, cuisine_id, str(ingredients)))
            conn.commit()
    

     def join_Cuisine(self, cur, conn):
        list_cuisines = []
        cur.execute('''SELECT Spoonacular.name, Tasty.name
        FROM Spoonacular
        INNER JOIN Tasty
        ON Spoonacular.cuisine_id = Tasty.cuisine_id''')
        for row in cur:
            list_cuisines.append(row)
            print(row)

    def get_edemam_database(self, ingredients):
        
        cur.execute(''' SELECT count(name) FROM sqlite_master WHERE type='table' AND name='Edemam' ''')
        if cur.fetchone()[0]==1:
            for recipie in ingredients:
                i = recipie
                carbs = self.get_carbs(recipie)
                fiber = self.get_fiber(recipie)
                calories = self.get_calories(recipie)
               cur.execute('''INSERT OR REPLACE INTO Edemam (ingredients, carbs, fiber, calories) VALUES (?, ?, ?, ?)''', (i, carbs, fiber, calories)) 
            conn.commit()

        else:
            cur.execute("CREATE TABLE Edemam (ingredients TEXT, carbs TEXT, fiber TEXT, calories TEXT)")
            for recipie in ingredients:
                i = recipie
                carbs = self.get_carbs(recipie)
                fiber = self.get_fiber(recipie)
                calories = self.get_calories(recipie)
                cur.execute('''INSERT OR REPLACE INTO Edemam (ingredients, carbs, fiber, calories) VALUES (?, ?, ?, ?)''', (i, carbs, fiber, calories))
            conn.commit()
    
    #input: type of cuisine
    #output: none
    #goes through get_ingredients and sets the 5 most popular ingredients equal to variables. 
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
            sorted_vals = sorted_dict.values()
        for i in sorted_vals[0:4]
            total += i
        return total 
    
    def top_ingredients_percents(self):
        r = get_ingredients_lst(cuisine)
        i1_percent = sorted_vals[0] / r
        i2_percent = sorted_vals[1] / r
        i3_percent = sorted_vals[2] / r
        i4_percent = sorted_vals[3] / r
        i5_percent = sorted_vals[4] / r
        other_amount = r - (i1_percent + i2_percent + i3_percent + i4_percent + i5_percent) 
        other_percent = other_amount / r


#input:none
#output: none
#Spoonacular bar graph of most popular cuisines and number of recipes.

    def spoonacular_visualization(self):
        r = Recipies()
        dict1 = r.get_dict()
        fig = plt.figure(figsize = (10, 5))
        ax1 = fig.add_subplot(121)
        ax1.bar([1,2,3], [3,4,5], color='pink')
        names = dict1.keys()
        values = dict1.values()
        plt.bar(names, values)
        plt.suptitle("Most Popular Cuisines")
        plt.show()

    #most popular ingredients
    #input: none
    #output: none
    #creates the pie chart breakdown of percent of recipes top 5 ingredients are in 
    def pie_chart(self):
        labels = i1, i2, i3, i4, i5, 'others'
        sizes = [self.i1_percent, self.i2_percent, self.i3_percent, self.i4_percent, self.i5_percent, self.other_percent]
        explode = (0, 0.1, 0, 0, 0, 0, 0, 0)
        fig1, ax1 = plt.subplots()
        ax1.pie(sizes, explode=explode, shadow=True, startangle=90)
        ax1.axis('equal') 
        plt.legend( loc = 'best', labels=['%s, %1.1f %%' % (l, s) for l, s in zip(labels, sizes)])
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
    
    #input: 
    #output:
    def netcarb_graph(self):
        carbs = get_carbs(self)
        fiber = get_fiber(self)
        values = range(0,50)
        fig = plt.figure(figsize = (10, 5))
        ax1 = fig.add_subplot(121)
        ax1.bar([1,2,3], [3,4,5], color='blue')
        ax2 = fig.add_subplot(121)
        ax2.bar([1,2,3], [3,4,5], color='yellow')
        #do i need both the ax plots and the fiber carb ones below?
        carb_bars = plt.bar(carbs, values, width = .5)
        fiber_bars = plt.bar(fiber, values, width = .5)
        plt.suptitle("Net Carbs of Ingredients")
        plt.show()

    #input: ingredients 
    #output: none
    #goes through the Edamam API to find the nutritional data of a given list of ingredients from get_ingredients.
    def get_nutrient_data(self, ingredients):
        url = "https://api.edamam.com/api/nutrition-data"
        lst = []

        for ingredient in ingredients:
            new_lst = []
            new_lst.append(ingredient)
    
            querystring = {"app_id": "e29147b2", "app_key": "b34772921762c60de0b5875b765b707a", "ingr": new_lst}

            response = requests.request("GET", url, params=querystring)
            response1 = json.loads(response.text)
            lst.append(response1)

        return lst
    
    # def get_nutrient_data(self, ingredients):
    #     url = "https://api.edamam.com/api/nutrition-data"
    #     querystring = {"app_id": "e29147b2", "app_key": "b34772921762c60de0b5875b765b707a", "ingr": ingredients}

    #     response = requests.request("GET", url, params=querystring)
            
    #     print(response.text)
    #     return response


    
    #input: ingredients 
    #output: none
    #goes through the edamam database to find the total carbs for a given ingredients list.
    
    def get_carbs(self, ingredients):
        count = 0
        r = self.get_nutrient_data(ingredients)
        for item in range(len(r)):
            if r[item]['totalNutrients'] != {}:
                carb_quan = r[item]['totalNutrients']["CHOCDF"]["quantity"]
                count += carb_quan
            else:
                print("No key")
        for item in range(len(r)):
            try:
                carb_units = r[item]['totalNutrients']["CHOCDF"]["unit"]
            except:
                carb_units = 'g'
        print(str(count) + carb_units)
        return str(count) + carb_units
        # if item['totalNutrients'] != {}:
        #         fat_quantity = item['totalNutrients']["FAT"]['quantity']
        #         count += fat_quantity
        #     else:
        #         print("no key")
        # print(count)
        # return str(count) + 'g'
        # try:
        #     count = 0
        #     r = self.get_nutrient_data(ingredients)
        #     data = json.loads(r.text)
        #     carb_units = data['totalNutrients']["CHOCDF"]['unit']
        #     for ingredient in ingredients:
        #         carb_quantity = data['totalNutrients']["CHOCDF"]['quantity']
        #         count += carb_quantity
        #         print(carb_quantity, ingredient)
        #     return str(count) + carb_units
        # except:
        #     return "data not found"

    #input: ingredients 
    #output: none
    #goes through the edamam database to find the total fiber for a given ingredients list.
    def get_fiber(self, ingredients):
        count = 0
        r = self.get_nutrient_data(ingredients)
        for item in range(len(r)):
            try:
                fiber_quan = r[item]['totalNutrients']["FIBTG"]["quantity"]
                count += fiber_quan
            except:
                print("No key")
        for item in range(len(r)):
            try:
                fiber_units = r[item]['totalNutrients']["FIBTG"]["unit"]
            except:
                fiber_units = 'g'
        print(str(count) +  fiber_units)
        return str(count) + fiber_units
    #input: ingredients 
    #output: none
    #goes through the edamam database to find the total calories for a given ingredients list.
    def get_calories(self, ingredients):
        count = 0
        r = self.get_nutrient_data(ingredients)
        print(r)
        for item in range(len(r)):
            try:
                calories = (r[item]['calories'])
                count += calories
            except:
                print("No key")
        print(count)
        return count


    def writeCalculations(self, cur, conn):
        path = os.path.dirname(os.path.abspath(__file__))
        f = open(path + "/Calculations.txt", "w+")

        #Categories Calculation 
        f.write("\nCuisine with the most recipies:\n\n")
        sql = "SELECT title FROM Categories"
        cur.execute(sql)
        dict_cuisine = {}
        for title in cur:
            if title not in dict_cuisine:
                dict_cuisine[title] = 0
                dict_cuisine[title] += 1
            else:
                dict_cuisine[title] += 1          
        sorted_dict = sorted(dict_cuisine.items(), reverse= True, key = lambda t: t[1])
        f.write("Most Recipies = " + sorted_dict[0] + "\n")


        f.write("\n\n############################################\n\n")

        #amount of recipies from spoonacular without a cuisine
        f.write("Amount of Recipies Without a Cuisine:\n\n")
        sql = "SELECT cuisine FROM Spoonacular"
        cur.execute(sql)
        count = 0
        for cuisine in cur:
            if cuisine == "Cuisine not classified":
                count += 1
                
        f.write("Amount of Recipies Without a Cuisine" + ": " + str(count) + "\n")

        f.write("\n\n############################################\n\n")

        #Tasty Calculation
        f.write("\nAverage of Ingredients List:\n\n")
        sql = "SELECT ingredients FROM Tasty"
        cur.execute(sql)
        recipies = 0
        ingredients = 0
        for r in cur:
            ing_list = list(r)
            ingredients += len(ing_list)
            recipies += 1
        avg = ingredients / recipies
        f.write("Average of Ingredients List = " + str(avg) + "\n")
        

        f.write("\n\n############################################\n\n")



#g = Recipies()
#g.get_fat("1 large apple")
#g.get_nutrient_data(['one large apple'])
#g.get_carbs(['one large apple'])


#g.get_carbs(['8 oz chicken breasts', 'seasoned breadcrumbs', 'Parmesan cheese'])
#g.get_calories(['8 oz chicken breasts', 'seasoned breadcrumbs', 'Parmesan cheese'])
#g.get_fiber(['1 teaspoon garlic powder', '1 teaspoon salt', '1 ½ cups crema table cream', '24 soft corn tortillas', 'Oil for frying', 'Crema', 'Cilantro', 'Cotija cheese', 'Avocado'])


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
   
        for ingredients in tasty:
            v.get_carbs(ingredients)
            v.get_fiber(ingredients)
            v.get_calories(ingredients)

if __name__ == "__main__":
    main()