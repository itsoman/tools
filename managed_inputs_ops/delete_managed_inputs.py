import requests
import configparser
import string
import random
import datetime
import json
import time
import os

def rand_gen(size, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))

i=0

workflows_array = {}

config = configparser.ConfigParser()
config.read('config.ini')
workflows_url = '/workflows'
authorize_url = '/auth/authorize'

id_token = ''
main_auth_url = ''
main_live_url = ''
aws_region = ''


class LIVE:

    def __init__(self):
        self.config = config
        self.get_main_url()
        self.get_main_live_url()
        self.get_aws_region()
        self.get_id_token()


    def get_id_token(self):
        global id_token
        if config.has_section("prod_credentials"):
            params = config.items("prod_credentials")
            credentials_dev = {}
            for param in params:
                credentials_dev[param[0]] = param[1]
            payload = credentials_dev
            full_url = main_auth_url + authorize_url
            print("Getting an ID Token...")
            try:
                response = requests.post(full_url, json=payload)
            except requests.exceptions.RequestException as exc:
                print("\nThe following error was returned: {}".format(exc))
                SystemExit(1)
            if response.status_code != 200:
                print("There is an error when trying to access the following endpoint {}, Status Code: {}, {}".format(full_url,response.status_code,response.text))
            else:
                json_response = json.loads(response.text)
                id_token = json_response["data"]["IdToken"]
        else:
            print("There is no dev_credentials section in the config file.\n")
            print("Aborting Operation")        


    def get_main_url(self):
        global main_auth_url
        if config.has_option('endpoints','auth_url'):
            main_auth_url = config.get('endpoints','auth_url')
        else:
            print("There is no auth_url option in the endpoints section of the config file.\n")

    def get_main_live_url(self):
        global main_live_url
        if config.has_option('endpoints','medialive_url'):
            main_live_url = config.get('endpoints','medialive_url')
        else:
            print("There is no medialive_url option in the endpoints section of the config file.\n")

    def get_aws_region(self):
        global aws_region
        if config.has_section('aws_region'):
            aws_region = config.get('aws_region','region')
        else:
            print('There is no aws_region section in the config file.\n')


    def cleanUpAllManagedInputs(self):
        print("Getting all Managed Inputs")
        inputsResponse = requests.get((main_live_url+"/managed-inputs"), headers = {'Authorization': id_token})
        inpResponse = json.loads(inputsResponse.text)
        jsonMnInputs = inpResponse["items"]
        for mInputs in range(len(jsonMnInputs)):
            print("Deleting Managed Input with ID: {}".format(jsonMnInputs[mInputs]["id"]))
            deleteResponse = requests.delete((main_live_url+"/managed-inputs/{}".format(jsonMnInputs[mInputs]["id"])), headers = {'Authorization': id_token})
            if deleteResponse.status_code != 204:
                print("Failed to delete managed input {} with error {} \n".format(jsonMnInputs[mInputs]["id"],deleteResponse.text))
                continue
            else:
                print("Status Code: {}, {} \n".format(deleteResponse.status_code, deleteResponse.text))

            
            

if __name__ == "__main__":
    live_test = LIVE()
    live_test.cleanUpAllManagedInputs()