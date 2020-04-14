import requests
import json
import sqlite3
import matplotlib
import matplotlib.pyplot as plt
import math
import numpy as np
import os


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


class Spoonacular:
 
    # def __init__(self, api_key, timeout=5, sleep_time=1.5, allow_extra_calls=False):
    #     """ Spoonacular API Constructor
    #     :param api_key: key provided by Spoonacular (str)
    #     :param timeout: time before quitting on response (seconds)
    #     :param sleep_time: time to wait between requests (seconds)
    #     :param allow_extra_calls: override the API call limit (bool)
    #     """
    #     assert api_key != 'd6138d2114b64120b05c0cbdb7c92f60'
    #     self.api_key = api_key
    #     self.api_root = "https://api.spoonacular.com/"
    #     self.timeout = timeout
    #     self.sleep_time = max(sleep_time, 1)  # Rate limiting TODO: Make this immutable
    #     self.allow_extra_calls = allow_extra_calls

    # def _make_request(self, path, method='GET', endpoint=None, query_=None, params_=None, json_=None):
    #     """ Make a request to the API """

    #     # Check if the API call cost will exceed the quota
    #     endpoint = inspect.stack()[1].function
    #     try:
    #         uri = self.api_root + path

    #         # API auth (temporary kludge)
    #         if params_:
    #             params_['apiKey'] = self.api_key
    #         else:
    #             params_ = {'apiKey': self.api_key}
    #         response = self.session.request(method, uri, timeout=self.timeout, data=query_, params=params_, json=json_)
    #     except socket.timeout as e:
    #         print("Timeout raised and caught: {}".format(e))
    #         return
    #     time.sleep(self.sleep_time)  # Enforce rate limiting
    #     return response

    #def _make_request(self, method='GET', params_=None, json_=None):
    # """ Make a request to the API """
    # uri = "https://api.spoonacular.com/"

        #params_ = {'apiKey': 'd6138d2114b64120b05c0cbdb7c92f60'}
        #response = self.session.request(method, uri,
        #                              timeout=self.timeout,
        #                              data=query_,
        #                              params=params_,
        #                             json=json_)
        #return response




    # def get_random_recipes(self, limitLicense=None, number=100, tags=None):
    #     """ Find random (popular) recipes.
    #     https://spoonacular.com/food-api/docs#get-random-recipes
    #     """
    #     endpoint = "recipes/random"
    #     url_query = {}
    #     url_params = {"limitLicense": limitLicense, "number": number, "tags": tags}
    #     return self._make_request(endpoint, method ='GET', query_=url_query, params_=url_params)
    
    def get_recipies(self):
        url = 'https://api.spoonacular.com/recipes/random'
        params = {"apiKey" : '3adec4cbad224f2c9596d4c011d346fc', "number" : "100"}
        response = requests.request("GET", url, params = params)
        print(response.text)
        #data = json.loads(r.text)
        return response.text

        #https://api.spoonacular.com/recipes/random?number=1&tags=vegetarian,dessert
# var1 = Spoonacular()
# var1.get_recipies()







# class Tasty:
#     def get_tasty_recipies(self):
#         url = "https://tasty.p.rapidapi.com/recipes/list"

#         querystring = {"from":"0","sizes":"100"}

#         headers = {'x-rapidapi-host': "tasty.p.rapidapi.com",'x-rapidapi-key': "74c1de20bdmsh109b356a35082c3p1cf14cjsn37f52eca5a61"}

#         response = requests.request("GET", url, headers=headers, params=querystring)

#         print(response.text)
#         return response.text

# var = Tasty()
# var.get_tasty_recipies()


# cuisinelist = ['american', 'italian', 'asian', 'mexican', 'southern', 'french', 'southwestern',
#             'barbecue-bbq', 'indian', 'chinese', 'cajun', 'mediterranean', 'greek', 'english',
#             'spanish', 'thai', 'german', 'moroccan', 'irish', 'japanese', 'cuban', 
#             'hawaiian', 'swedish', 'hungarian', 'portuguese']
# resultsPerCuisine = 500

# create wrapper function
# def recipeOutputter(cuis):
#     scuisine = '&allowedCuisine[]=cuisine^cuisine-' + cuis
#     sresults = '&maxResult=' + str(resultsPerCuisine)
    
#     # retrieve and store results in a DataFrame
#     r = (requests.get('http://api.yummly.com/v1/api/recipes?' + cykey + scuisine + sresults)).json()
#     recipes = pd.DataFrame(r['matches'], columns = ['id', 'recipeName', 'rating', 'totalTimeInSeconds', 'ingredients'])
    
#     # extract course and cusine and add to DF
#     course = []
#     cuisine = []
#     for i in r['matches']:
#         course.append(i['attributes'].get('course', None))
#         cuisine.append(i['attributes'].get('cuisine', None))
#     recipes['course'] = course
#     recipes['cuisine'] = cuisine
    
#     # rearrange DF
#     recipes.set_index('id', inplace=True)
#     col = ['recipeName', 'rating', 'totalTimeInSeconds', 'course', 'cuisine', 'ingredients']
#     recipes=recipes[col]
#     https://api.spoonacular.com/recipes/random?number=1&tags=vegetarian,dessert

class Tasty:
    def get_tasty_recipies(self):
        url = "https://tasty.p.rapidapi.com/recipes/list"

        querystring = {"from":"0","sizes":"100"}

        headers = {'x-rapidapi-host': "tasty.p.rapidapi.com",'x-rapidapi-key': "74c1de20bdmsh109b356a35082c3p1cf14cjsn37f52eca5a61"}

        response = requests.request("GET", url, headers=headers, params=querystring)

        return response

    def get_dict(self):
        dict1 = {}
        r = self.get_tasty_recipies()
        data = json.loads(r.text)
        for val in range(len(data['results'])):
            try:
                for tag in data['results'][val]["tags"]:
                    if tag['type'] == 'cuisine': 
                        x = tag['display_name']
                        if x not in dict1:
                            dict1[x] = 0
                        dict1[x] += 1
                        break
                    else:
                        if tag['type'] == 'dietary':
                            x = tag['display_name']
                            if x not in dict1:
                                dict1[x] = 0
                            dict1[x] += 1 
            except:
                x = "Cuisine not classified"     
                if x not in dict1:
                    dict1[x] = 0
                dict1[x] += 1   
        print(dict1)
        return dict1

var = Tasty()
var.get_dict()