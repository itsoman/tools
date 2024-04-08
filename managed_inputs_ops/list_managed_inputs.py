import requests
import configparser
import string
import random
import json

def rand_gen(size, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))

config = configparser.ConfigParser()
config.read('../configs/managed_inputs_ops/config.ini')
managed_inputs_url = '/managed-inputs/'
authorize_url = '/auth/authorize'
managed_input_id = ''

id_token = ''
main_auth_url = ''
main_live_url = ''


class MANAGEDINPUTS:

    def __init__(self):
        self.config = config
        self.get_main_url()
        self.get_main_live_url()
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
            print("There is no prod_credentials section in the config file.\n")
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


    def list_managed_inputs(self):
        managed_inp = ''
        full_url = main_live_url + managed_inputs_url
        print("Getting a list of all managed inputs...\n")
        try:
            managed_inp = requests.get((full_url), headers = {'Authorization': id_token})
            if managed_inp.status_code != 200:
                print("Error when listing managed-inputs, the following response has been returned by the {} endpoint, status code: {}, {}".format(full_url,managed_inp.status_code,managed_inp.text))
            else:
                managedinputs_array = json.loads(managed_inp.text)
                print(managedinputs_array["items"])
                return managedinputs_array
        except requests.exceptions.RequestException as exc:
            print("\nThe following error has been returned:\n{}".format(exc))
            SystemExit(1)




if __name__ == "__main__":
    live_test = MANAGEDINPUTS()
    live_test.list_managed_inputs()