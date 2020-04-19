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
        params = {"apiKey" : '9b08f9ce44274ec4a952ff296062f655', "number" : "20"}
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
        return dict1
    
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
        try:
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
        except:
            pass
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
                cur.execute("INSERT OR IGNORE INTO Categories (id,title) VALUES (?,?)",(i,cuisines[i]))
            conn.commit()
        else:
            cur.execute("CREATE TABLE Categories (id INTEGER PRIMARY KEY, title TEXT)")
            for i in range(len(cuisines)):
                cur.execute("INSERT OR IGNORE INTO Categories (id,title) VALUES (?,?)",(i,cuisines[i]))
            conn.commit()

    
    #input: type of cuisine, cursor and conncetion to the database to create a table within it
    #output: creates tasty table in database --> look below for description
    #sets up the Tasty table within the database, if table exists, then only add to the existing database  

    def get_tasty_database(self, cuisine, cur, conn):
        r = self.get_tasty_recipes(cuisine)
        try:
            data = json.loads(r.text)
            cur.execute(''' SELECT count(name) FROM sqlite_master WHERE type='table' AND name='Tasty' ''')
            if cur.fetchone()[0]==1:
                try:
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
                        cur.execute('''INSERT OR IGNORE INTO Tasty (recipe_id, name, cuisine, cuisine_id, ingredients) VALUES (?, ?, ?, ?, ?)''', (recipe_id, name, c, cuisine_id, str(ingredients)))
                    conn.commit()
                except:
                    pass
            else:
                cur.execute('''CREATE TABLE Tasty (recipe_id TEXT PRIMARY KEY, name TEXT, cuisine TEXT, cuisine_id INTEGER, ingredients TEXT)''')
                try:
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
                        cur.execute('''INSERT OR IGNORE INTO Tasty (recipe_id, name, cuisine, cuisine_id, ingredients) VALUES (?, ?, ?, ?, ?)''', (recipe_id, name, c, cuisine_id, str(ingredients)))
                    conn.commit()
                except:
                    pass
        except:
            print("Ran into JSON decode error")
    #input: cursor and conncetion to the database to create a table within it
    #output: creates spoonacular table in database --> look below for description
    #sets up the Spoonacular table within the database, if table exists, then only add to the existing database  

    def get_spoon_database(self, cur, conn):
        r = self.get_recipies()
        try:
            data = json.loads(r.text)
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
                    cur.execute('''INSERT OR IGNORE INTO Spoonacular (recipe_id, name, cuisine, cuisine_id, ingredients) VALUES (?, ?, ?, ?, ?)''', (recipe_id, name, cuisine, cuisine_id, str(ingredients)))
                conn.commit()
            else:
                cur.execute('''CREATE TABLE IF NOT EXISTS Spoonacular (recipe_id TEXT PRIMARY KEY, name TEXT, cuisine TEXT, cuisine_id INTEGER, ingredients TEXT)''')
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
                    cur.execute('''INSERT OR IGNORE INTO Spoonacular (recipe_id, name, cuisine, cuisine_id, ingredients) VALUES (?, ?, ?, ?, ?)''', (recipe_id, name, cuisine, cuisine_id, str(ingredients)))
                conn.commit()
        except:
            print("Ran into Json Decode Error")
   
    #input: cursor, conncetion, and a list of ingredients 
    #output: creates a Edamam table in database --> look below for description
    #sets up the Edamam table within the database, if table exists, then only add to the existing database  

    def get_edemam_database(self, cur, conn, ingredients):
        
        cur.execute(''' SELECT count(name) FROM sqlite_master WHERE type='table' AND name='Edemam' ''')
        if cur.fetchone()[0]==1:
            i = str(ingredients)
            carbs = self.get_carbs(ingredients)
            fiber = self.get_fiber(ingredients)
            calories = self.get_calories(ingredients)
            cur.execute('''INSERT OR IGNORE INTO Edemam (ingredients, carbs, fiber, calories) VALUES (?, ?, ?, ?)''', (i, carbs, fiber, calories)) 
            conn.commit()

        else:
            cur.execute("CREATE TABLE Edemam (ingredients TEXT, carbs TEXT, fiber TEXT, calories TEXT)")
            i = str(ingredients)
            carbs = self.get_carbs(ingredients)
            fiber = self.get_fiber(ingredients)
            calories = self.get_calories(ingredients)
            cur.execute('''INSERT OR IGNORE INTO Edemam (ingredients, carbs, fiber, calories) VALUES (?, ?, ?, ?)''', (i, carbs, fiber, calories))
            conn.commit()
    
    #input: cursor and conncetion to the database 
    #output: joins the Tasty column in names with the carbs column in Edamam by their shared ingredients


    def join_recipies(self, cur, conn):
        list_names = []
        cur.execute('''SELECT Tasty.name, Tasty.cuisine FROM Tasty JOIN Spoonacular ON Tasty.cuisine_id = Spoonacular.cuisine_id''')
        for row in cur:
            list_names.append(row)
            print(row)



    #input: type of cuisine
    #output: returns the top most common ingredients and sorts the values of the ingredients dictionary
    #goes through get_ingredients and sets the 5 most popular ingredients equal to variables. 
    def get_ingredients_lst(self, cuisine):
        ingredients = self.get_ingredients(cuisine)
        ingredients_dict= {}
        try:
            for x in ingredients:
                for y in x: 
                    if y in ingredients_dict: 
                        ingredients_dict[y] += 1
                    else: 
                        ingredients_dict[y] = 0 
                        ingredients_dict[y] += 1
            sorted_dict = sorted(ingredients_dict.items(), key = lambda x: x[1], reverse=True)
            print(sorted_dict)
            i1 = sorted_dict[0]
            i2 = sorted_dict[1]
            i3 = sorted_dict[2]
            i4 = sorted_dict[3]
            i5 = sorted_dict[4]
        except:
            pass
        return sorted_dict
        

    #input: none
    #output: sets the top most common ingredients and sorts the values of the ingredients dictionary
    #divides how

    def top_ingredients_percents(self, cuisine):
        r = self.get_ingredients_lst(cuisine)
        total = 0
        try:
            for i in r[0:4]:
                for x in i:
                    total += i[1] 
            i1_percent = r[0][1] / total
            i2_percent = r[1][1] / total
            i3_percent = r[2][1] / total
            i4_percent = r[3][1] / total
            i5_percent = r[4][1] / total
            other_amount = total - (i1_percent + i2_percent + i3_percent + i4_percent + i5_percent) 
            other_percent = other_amount / total
            return [i1_percent, i2_percent, i3_percent, i4_percent, i5_percent, other_percent]
        except:
            pass


    #input: none
    #output: Spoonacular bar graph of most popular cuisines and number of recipes.

    def spoonacular_visualization(self):
        dict1 = self.get_dict()
        fig = plt.figure(figsize = (10, 5))
        ax1 = fig.add_subplot(121)
        names = dict1.keys()
        values = dict1.values()
        ax1.bar(names, values, color='pink')
        plt.xticks(rotation=45, size= 6)
        plt.suptitle("Most Popular Cuisines")
        plt.show()

    
    #input: none
    #output: Tasty Pie chart breakdown of percentage of recipes top 5 ingredients are in 
    def pie_chart(self, cuisine):
        v = self.get_ingredients_lst(cuisine)
        r = self.top_ingredients_percents(cuisine)
        try:
            labels = v[0], v[1], v[2], v[3], v[4], 'Others'
            sizes = [r[0], r[1], r[2], r[3], r[4], r[5]]
            explode = (0, 0, 0, 0, 0, 0.1)
            fig1, ax1 = plt.subplots()
            ax1.pie(sizes, explode=explode, shadow=True, startangle=90)
            ax1.axis('equal') 
            plt.legend( loc = 'best', labels=['%s, %1.1f %%' % (l, s) for l, s in zip(labels, sizes)])
            plt.title("Pie Chart of Most Popular Ingredients")
            plt.show()
        except:
            pass


    #input: none
    #output: 
    # calories and ingredients
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
    def netcarb_graph(self, ingredients):

        carbs = self.get_carbs(ingredients)
        
        fiber = self.get_fiber(ingredients)


        
        ind = np.arange(1)
        width = 0.05
        
        plt.title("Net Carbs of Recipe")
        #x = np.arange(len(carbs))
        plt.bar(ind, carbs, width, color = 'blue')
        #carb_bars = plt.bar(carbs, width, height, color='blue')
       # y = np.arange(len(fiber))
        plt.bar(ind, fiber, width, bottom=carbs, color='yellow')
        # plt.yticks(np.arange(0, 50, 5))
        plt.ylabel('Nutrient in Grams')
        plt.xticks(ind, ("recipe",))
        #plt.set_xticks(ind, (recipe))
        plt.xlabel('Tasty Recipe')
        plt.legend(labels=['Carb', 'Fiber'])
        #plt.legend((carbs, fiber), ('Carbs', 'Fiber'))
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
    
            querystring = {"app_id": "7e84e824", "app_key": "3ad7d55a21c8dfe344d9ce7778aa48fe", "ingr": new_lst}

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
        return count 

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
        # for item in range(len(r)):
        #     try:
        #         fiber_units = r[item]['totalNutrients']["FIBTG"]["unit"]
        #     except:
        #         fiber_units = 'g'
        return count

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
        for t in cur:
            title = t[0]
            if title not in dict_cuisine:
                dict_cuisine[title] = 0
                dict_cuisine[title] += 1
            else:
                dict_cuisine[title] += 1          
        sorted_dict = sorted(dict_cuisine.items(), reverse= True, key = lambda t: t[1])
        f.write("Most Recipies = " + str(sorted_dict[0][0]) + "\n")


        f.write("\n\n############################################\n\n")

        #amount of recipies from spoonacular without a cuisine
        f.write("Amount of Recipies Without a Cuisine:\n\n")
        sql = "SELECT cuisine FROM Spoonacular"
        cur.execute(sql)
        count = 0
        for c in cur:
            cuisine = c[0]
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
        if recipies != 0:
            avg = ingredients / recipies
        else:
            avg = ingredients
        f.write("Average of Ingredients List = " + str(avg) + "\n")
        

        f.write("\n\n############################################\n\n")

        #Edamam Calculation
        f.write("\nRecipe with the Highest Calorie Count:\n\n")
        sql = "SELECT ingredients, calories FROM Edemam"
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
    cuisines = v.get_dict().keys()

    v.setUpCategoriesTable(cur, conn)
    #set up or accumulate to the spoonacular table
    v.get_spoon_database(cur, conn)

    r_list = []
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
        r_list.append(r)
        tasty = v.get_ingredients(r)
        

        #set up or accumulate to the tasty table
        v.get_tasty_database(r, cur, conn)
        # v.pie_chart(r)
   
        #calls edamam and netcarb  
        for ingredients in tasty:
            v.get_edemam_database(cur, conn, ingredients)
            # v.netcarb_graph(ingredients)

    #calls calculations
    v.writeCalculations(cur, conn)

 #calls join recipies
    v.join_recipies(cur, conn)

    random_index = random.randrange(len(r_list))
# # #calls visualizations
    #calls pie chart
    # v.pie_chart(r_list[random_index])

    v.spoonacular_visualization()

# #     #calls generate scatter
#     v.generate_scatter()


if __name__ == "__main__":
    main()