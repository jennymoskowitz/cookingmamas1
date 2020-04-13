import json
import unittest
import os
import requests

API_KEY = 'd6138d2114b64120b05c0cbdb7c92f60'
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

def get_cuisine(cuisine):
    #spoontacular API
    #cuisine_list = ["African", "American", "British", "Cajun", "Caribbean", "Chinese", "Eastern European", "European",
    #"French", "German", "Greek", "Indian", "Irish", "Italian", "Japanese", "Jewish", "Korean", "Latin American", 
    #"Mediterranean", "Mexican", "Middle Eastern", "Nordic", "Southern", "Spanish", "Thai", "Vietnamese"]
    #"?apiKey=" + API_KEY + 
    #num = '10'
    #+ "?number" + num
    base_url = 'https://api.spoonacular.com/'
    endpoint = 'recipies/search'
    params = "?cuisine" + cuisine
    r = requests.get((base_url + endpoint + params))
    data = json.loads(r.text)
    print(data)

#def _make_request(self, path, method='GET', endpoint=None,
                      #query_=None, params_=None, json_=None):
        #""" Make a request to the API """

    
    #uri = self.api_root + path

        # API auth (temporary kludge)
    #if params_:
        #params_['apiKey'] = self.api_key
    #else:
        #params_ = {'apiKey': self.api_key}
   # response = self.session.request(method, uri,
          #                          timeout=self.timeout,
          #                          data=query_,
           #                         params=params_,
           #                         json=json_)
    #return response


def classify_cuisine(self, cuisine):
    
        endpoint = "recipes/cuisine"
        url_query = {"cuisine": cuisine}
        url_params = {}
        try:
            return self._make_request(endpoint, method="POST", query_=url_query, params_=url_params
        except:
            print("Cuisine not found")


classify_cuisine("Greek")

#Tasty API 

def get_recipes(self, title):
    url = "https://tasty.p.rapidapi.com/recipes/list"

    querystring = {,"q":"{}","from":"0","sizes":"20"}

    headers = {
        'x-rapidapi-host': "tasty.p.rapidapi.com",
        'x-rapidapi-key': "74c1de20bdmsh109b356a35082c3p1cf14cjsn37f52eca5a61"
        }

    response = requests.request("GET", url, headers=headers, params=querystring)

    print(response.text)

def get_similarities(self, recipie):
    url = "https://tasty.p.rapidapi.com/recipes/list-similarities"

    querystring = {"recipe_id":"5586"}

    headers = {
        'x-rapidapi-host': "tasty.p.rapidapi.com",
        'x-rapidapi-key': "74c1de20bdmsh109b356a35082c3p1cf14cjsn37f52eca5a61"
        }

    response = requests.request("GET", url, headers=headers, params=querystring)

    print(response.text)





