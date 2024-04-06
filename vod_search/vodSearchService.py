import requests
import json

import configparser
config = configparser.ConfigParser()
config.read('config.ini')




class Search:
       
    def __init__(self):
        global endpoints
        global dict_endpoints
        endpoints = config.items('endpoints') 
        dict_endpoints = dict((x, y) for x, y in endpoints)
        

    def searchEndpoint(self):
        searchEndpoint = dict_endpoints['searchendpoint']
        baseEndpoint = dict_endpoints['baseendpoint']
        fullUrl = baseEndpoint + searchEndpoint
        data = {
                    "query": {
	                            "multi_match": {
	                                    "query": "test"
	                                    }
                            }
                }
        response = requests.post(fullUrl, json=data)
        json_data = json.loads(response.text)
        print(json.dumps(json_data, indent=4, sort_keys=True))



if __name__ == "__main__":
    search = Search()
    search.searchEndpoint()