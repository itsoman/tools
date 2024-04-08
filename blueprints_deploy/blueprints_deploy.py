import requests
import configparser
import json
import enquiries


workflows_array = {}
options = {}

config = configparser.ConfigParser()
config.read('../configs/blueprints_deploy/config.ini')
authorize_url = '/auth/authorize' #this could be added to the config file

id_token = '' #this can be declared in the class
main_auth_url = ''#this can be declared in the class
aws_region = ''#this can be declared in the class

git_payload_request = {}


class DEPLOYING:

    def __init__(self):
        self.config = config
        self.get_git_credentials()
        self.dispatch_func()


    def get_id_token(self, env_var):
        global id_token
        if config.has_section("credentials_%s" %env_var): #use try/except
            params = config.items("credentials_%s" %env_var)
            credentials_dev = {}
            for param in params:
                credentials_dev[param[0]] = param[1]
            payload = credentials_dev #not needed
            full_url = main_auth_url + authorize_url
            print("Getting %s ID Token..." %env_var)
            try:
                response = requests.post(full_url, json=payload)
            except requests.exceptions.RequestException as exc:
                print("\nThe following error was returned: {}".format(exc))
                SystemExit(1)
            if response.status_code != 200: #this can be in the exeption
                print("There is an error when trying to access the following endpoint {}, Status Code: {}, {}".format(full_url,response.status_code,response.text))
                # f"bla bla{prom}, bla {prom2}"
            else: #this can be in the try
                json_response = json.loads(response.text)
                id_token = json_response["data"]["IdToken"] #json_response.get("data").get("IdToken")
        else:
            print("There is no dev_credentials section in the config file.\n")
            print("Aborting Operation")        


    def get_main_url(self, env_var):
        global main_auth_url
        if config.has_option('endpoints','auth_url_%s' % env_var):
            main_auth_url = config.get('endpoints','auth_url_%s' % env_var)
        else:
            print("There is no auth_url option in the endpoints section of the config file.\n")

    def get_aws_region(self):
        global aws_region
        if config.has_section('aws_region'):
            aws_region = config.get('aws_region','region')
        else:
            print('There is no aws_region section in the config file.\n')

    def get_git_credentials(self):
        global git_token
        global git_url
        if config.has_section('git_credentials'):
            git_token = config.get('git_credentials','git_token')
            git_url = config.get('git_credentials', 'git_url')
        else:
            print('There is no git_credentials section in the config file.\n')



    def get_all_organizations_and_initiate_deploy_to_organization(self):
        global git_payload_request
        global main_auth_url
        global id_token
        global options
        options = {}
        headers = {'Authorization': id_token}
        orgs_list = requests.get(main_auth_url+'/organizations',headers=headers)
        orgs_list_json = json.loads(orgs_list.text)

        for organization in range(len(orgs_list_json['data'])):
            options[orgs_list_json['data'][organization]['name']] = orgs_list_json['data'][organization]['guid']

        header_message = "Choose organization:"
        chosen_org_id = DEPLOYING.menu_display(self,options,header_message)
        payload_request_string = git_payload_request['variables[COMMAND]']
        git_payload_request['variables[COMMAND]'] = payload_request_string.replace('--organization-id=','--organization-id=%s'%chosen_org_id)
        DEPLOYING.deploy_bps_for_org(self)


    def deploy_bps_for_org(self):
        global git_payload_request
        global git_url
        print("Deploying blueprints...")
        print(git_url)
        print(git_payload_request)
        # req_deploy = requests.post(git_url,data=git_payload_request)

    def menu_display(self, options, header_message):
        options['Exit'] = 0
        choice = enquiries.choose(header_message, options)
        if choice == 0:
            exit()
        else:
            return choice

    def dispatch_func(self):
        global git_token
        global git_payload_request
        options['Staging'] = 'stg'
        options['Production'] = 'prod'
        options['Exit'] = 0
        header_message = 'Choose environment: '
        decision = DEPLOYING.menu_display(self,options,header_message)
        DEPLOYING.get_main_url(self, decision)
        DEPLOYING.get_id_token(self, decision)
        git_payload_request = {
        'token': git_token, 
        'ref':'develop',
        'variables[COMMAND]':'./deploy.sh --aws-profile=ioio-tv-%s --region=us-east-1 --organization-id= --environment=%s' %(decision,decision),
        'variables[PROJECT]':'live-blueprints'
        }
        


if __name__ == "__main__":
    deploy_bps = DEPLOYING()
    i=0
    while i <= 1:
        deploy_bps.get_all_organizations_and_initiate_deploy_to_organization()