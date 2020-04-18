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
    #output: returns the response object for Spoonacular API
    #goes through the Spoonacular API to find 100 random recipies
    def get_recipies(self):
        url = 'https://api.spoonacular.com/recipes/random'
        params = {"apiKey" : '3adec4cbad224f2c9596d4c011d346fc', "number" : "20"}
        response = requests.request("GET", url, params = params)

        return response

    #input: none
    #output: returns the dictionary keys
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
            # else:
            #     print("Cuisine not found.")
        return dict1.keys()
    
    #input: type of cuisine
    #output: returns the response object for Tasty API
    #goes through the tasty API to return 20 recipes of the given cuisine. 
    def get_tasty_recipes(self, cuisine):
        url = "https://tasty.p.rapidapi.com/recipes/list"
 
        querystring = {"tags": cuisine, "from": 0,"sizes": 20}

        headers = {'x-rapidapi-host': "tasty.p.rapidapi.com",'x-rapidapi-key': "4815cec8ebmsh228e04eb0078c6fp11b92fjsnfb175b8eb0a0"}

        response = requests.request("GET", url, headers=headers, params=querystring)

        return response

    #input: type of cuisine
    #output: Returns a list of the cuisine ingredients
    #goes through the tasty database given the specified cuisine. 
    def get_ingredients(self, cuisine):
        cuisine_ingredients = []
        r = self.get_tasty_recipes(cuisine)
        data = json.loads(r.text)
        for x in range(len(data['results'][0:4])):
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

    #input: cursor and conncetion to the database to create a table within it
    #output: creates categories table for Spoonacular in database --> look below for description
    #sets up the categories table for Spoonacular within the database, if table exists, then only add to the existing database  
    def setUpCategoriesTable(self, cur, conn):
        cuisines = ["African", "American", "British", "Cajun", "Caribbean", "Chinese", "Eastern European", "European",
        "French", "German", "Greek", "Indian", "Irish", "Italian", "Japanese", "Jewish", "Korean", "Latin American", 
        "Mediterranean", "Mexican", "Middle Eastern", "Nordic", "Southern", "Spanish", "Thai", "Vietnamese", "Cuisine not classified"]
        cur.execute("DROP TABLE IF EXISTS Categories")
        cur.execute(''' SELECT count(name) FROM sqlite_master WHERE type='table' AND name='Categories' ''')
        if cur.fetchone()[0]==1:
            for i in range(len(cuisines)):
                cur.execute("INSERT OR REPLACE INTO Categories (id,title) VALUES (?,?)",(i,cuisines[i]))
            conn.commit()
        else:
            cur.execute("CREATE TABLE Categories (id INTEGER PRIMARY KEY, title TEXT)")
            for i in range(len(cuisines)):
                cur.execute("INSERT OR REPLACE INTO Categories (id,title) VALUES (?,?)",(i,cuisines[i]))
            conn.commit()

    
    #input: type of cuisine, cursor and conncetion to the database to create a table within it
    #output: creates tasty table in database --> look below for description
    #sets up the Tasty table within the database, if table exists, then only add to the existing database  

    def get_tasty_database(self, cuisine, cur, conn):
        r = self.get_tasty_recipes(cuisine)
        data = json.loads(r.text)
        cur.execute("DROP TABLE IF EXISTS Tasty")
        cur.execute(''' SELECT count(name) FROM sqlite_master WHERE type='table' AND name='Tasty' ''')
        if cur.fetchone()[0]==1:
            for x in range(4):
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
                cuisine_id = 0
                for row in cur:
                    i = row[0]
                    n = row[1]
                    if n == c:
                        cuisine_id = i
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
            for x in range(4):
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
                cuisine_id = 0
                for row in cur:
                    i = row[0]
                    n = row[1]
                    if n == c:
                        cuisine_id = i
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
    #output: creates spoonacular table in database --> look below for description
    #sets up the Spoonacular table within the database, if table exists, then only add to the existing database  

    def get_spoon_database(self, cur, conn):
        r = self.get_recipies()
        data = json.loads(r.text)
        cur.execute("DROP TABLE IF EXISTS Spoonacular")
        cur.execute(''' SELECT count(name) FROM sqlite_master WHERE type='table' AND name='Spoonacular' ''')
        if cur.fetchone()[0]==1:
            for x in range(len(data['recipes'])): #run 20 each time
                recipe_id = data['recipes'][x]["id"]
                name = data['recipes'][x]['title']
                if len(data['recipes'][x]['cuisines']) > 0:
                    cuisine = data['recipes'][x]['cuisines'][0]
            
                else:
                    cuisine = "Cuisine not classified"
                cur.execute('SELECT * FROM Categories')
                cuisine_id = 0
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
        else:
            cur.execute('''CREATE TABLE Spoonacular (recipe_id TEXT PRIMARY KEY, name TEXT, cuisine TEXT, cuisine_id INTEGER, ingredients TEXT)''')
            for x in range(len(data['recipes'])):
                recipe_id = data['recipes'][x]["id"]
                name = data['recipes'][x]['title']
                if len(data['recipes'][x]['cuisines']) > 0:
                    cuisine = data['recipes'][x]['cuisines'][0]
            
                else:
                    cuisine = "Cuisine not classified"
                cur.execute('SELECT * FROM Categories')
                cuisine_id = 0
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
    
   
    #input: cursor, conncetion, and a list of ingredients 
    #output: creates a Edamam table in database --> look below for description
    #sets up the Edamam table within the database, if table exists, then only add to the existing database  

    def get_edemam_database(self, cur, conn, ingredients):
        
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
    
    #input: cursor and conncetion to the database 
    #output: joins the Tasty column in names with the carbs column in Edamam by their shared ingredients


    def join_Ingredients(self, cur, conn):
        list_ingredients = []
        cur.execute('''SELECT Tasty.name, Edamam.carbs
        FROM Tasty
        INNER JOIN Edamam
        ON Tasty.ingredients = Edamam.ingredients''')
        for row in cur:
            list_ingredients.append(row)
            print(row)



    #input: type of cuisine
    #output: returns the top most common ingredients and sorts the values of the ingredients dictionary
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
        for i in sorted_vals[0:4]:
            total += i
        return total 

    #input: none
    #output: sets the top most common ingredients and sorts the values of the ingredients dictionary
    #divides how

    def top_ingredients_percents(self):
        r = get_ingredients_lst(cuisine)
        i1_percent = sorted_vals[0] / r
        i2_percent = sorted_vals[1] / r
        i3_percent = sorted_vals[2] / r
        i4_percent = sorted_vals[3] / r
        i5_percent = sorted_vals[4] / r
        other_amount = r - (i1_percent + i2_percent + i3_percent + i4_percent + i5_percent) 
        other_percent = other_amount / r


    #input: none
    #output: Spoonacular bar graph of most popular cuisines and number of recipes.

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

    
    #input: none
    #output: Tasty Pie chart breakdown of percentage of recipes top 5 ingredients are in 
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
    #output: creates the histogram of Average Calories by Cuisine Type
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

    #input: none
    #output: 
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
    #output: returns list of nutritional data based on ingredients list from get_ingredients
    #goes through the Edamam API to find the nutritional data of a given list of ingredients from get_ingredients.
    def get_nutrient_data(self, ingredients):
        url = "https://api.edamam.com/api/nutrition-data"
        lst = []

        for ingredient in ingredients:
            new_lst = []
            new_lst.append(ingredient)
    
            querystring = {"app_id": "3ab5445f", "app_key": "e8238ffb38bc0b9ea027ea242c28476f", "ingr": new_lst}

            response = requests.request("GET", url, params=querystring)
            response1 = json.loads(response.text)
            lst.append(response1)
        return lst

    
    #input: ingredients 
    #output: returns total carb count for a given ingredients list
    #goes through the edamam database to find the total carbs for a given ingredients list.
    
    def get_carbs(self, ingredients):
        count = 0
        r = self.get_nutrient_data(ingredients)
        for item in range(len(r)):
            try:
                carb_quantity = r[item]['totalNutrients']["CHOCDF"]["quantity"]
                count += carb_quantity
            except:
                y = "no key"
        for item in range(len(r)):
            try:
                carb_units = r[item]['totalNutrients']["CHOCDF"]["unit"]
            except:
                carb_units = 'g'
        return str(count) + carb_units

    #input: ingredients 
    #output:  returns total fiber count for a given ingredients list
    #goes through the edamam database to find the total fiber for a given ingredients list.
    def get_fiber(self, ingredients):
        count = 0
        r = self.get_nutrient_data(ingredients)
        for item in range(len(r)):
            try:
                fiber_quan = r[item]['totalNutrients']["FIBTG"]["quantity"]
                count += fiber_quan
            except:
                py = "no key"
        for item in range(len(r)):
            try:
                fiber_units = r[item]['totalNutrients']["FIBTG"]["unit"]
            except:
                fiber_units = 'g'
        return str(count) + fiber_units

    #input: ingredients 
    #output:  returns total calorie count for a given ingredients list
    #goes through the edamam database to find the total calories for a given ingredients list.
    def get_calories(self, ingredients):
        count = 0
        r = self.get_nutrient_data(ingredients)
        for item in range(len(r)):
            try:
                calories = (r[item]['calories'])
                count += calories
            except:
                y = "no key"
        return count

    #input: cursor and conncetion to the database to access its data
    #output: returns calculations from the data in each of the tables 
    #for categories we calculate which cuisine has the most recipes for spoonacular we calculate number of recipes that don't have a cuisine 
    #and from Tasty we calulate the average length of the ingredient list
    #and from Edamam the greatest number of calories found in a given recipe
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

        #Edamam Calculation
        f.write("\nRecipe with the Highest Calorie Count:\n\n")
        sql = "SELECT ingredients, calories FROM Edamam"
        cur.execute(sql)
        max_calories = 0
        for r in cur:
            ingredients = r[0]
            calories = int(r[1])
            if calories > max_calories:
                max_calories = calories
        
        f.write("The Highest Calories is = " + str(max_calories) + "\n")


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

    v.setUpCategoriesTable(cur, conn)
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
   
# #         #calls edamam and netcarb  
        for ingredients in tasty:
            a = v.get_carbs(ingredients)
            print(a)
            b = v.get_fiber(ingredients)
            print(b)
            c = v.get_calories(ingredients)
            print(c)
            # v.netcarb_graph(ingredients)

# #     #calls calculations
    # v.writeCalculations(cur, conn)

# #     #calls join ingredients
#     v.join_Ingredients(cur, conn)

# # #calls visualizations
# #     #calls pie chart
#     v.pie_chart()

# #     #calls price histogram
#     v.priceHistogram(cur, conn)

# #     #calls generate scatter
#     v.generate_scatter()


if __name__ == "__main__":
    main()