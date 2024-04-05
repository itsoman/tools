import datetime
import configparser
import requests
import json
import os
import boto3
from boto3.s3.transfer import TransferConfig

config = configparser.ConfigParser()
config.read('config.ini')

bucket_name = ""
post_data = {
  "meta": {
    "type": "source",
    "title": "Python_Upload_{}".format(datetime.datetime.now()),
    "encodeLater": "1",
    "vodThumbsCapturePeriod": "7",
    "vodThumbsCaptureHeight": "128"
  }
}
meta_guid = ""

class UPLOAD:

    def __init__(self):
        self.config = config
        self.get_config_stuff()

    def get_config_stuff(self):
        global base_url
        global api_key
        global multipart_upload
        global create_metadata
        global aws_access_key
        global aws_secret_key

        if config.has_section('endpoints'):
            base_url = config.get('endpoints','base_url')
            multipart_upload = config.get('endpoints','multipart_upload')
            create_metadata = config.get('endpoints','create_metadata')
        else:
            print("There is no endpoints section or there is a missing endpoint the config file.\n")
            exit()

        if config.has_option('credentials','api_key'):
            api_key = config.get('credentials','api_key')
        else:
            print("There is no api key option in the credentials section of the config file.\n")
            exit()

        if config.has_option('credentials','aws_access_key') and config.has_option('credentials','aws_secret_access_key'):
            aws_access_key = config.get('credentials','aws_access_key')
            aws_secret_key = config.get('credentials','aws_secret_access_key')
        else:
            print("Missing AWS access key or secret key from config file")
            exit()

    def getSettings(self):
        global bucket_name
        print("Getting Upload Settings...")
        headers = {'accept':'application/json', 'x-api-key': api_key}
        full_url = base_url + multipart_upload
        response = requests.get(full_url, headers=headers)
        bucket_name = json.loads(response.text)["data"]["bucket"]


    def create_metadata(self):
        print("Creating Metadata...")
        global meta_guid
        headers = {'Content-Type':'application/json', 'Accept':'application/json', 'x-api-key': api_key}
        full_url = base_url + create_metadata
        response = requests.post(full_url, json=post_data, headers=headers)
        json_response = json.loads(response.text)
        meta_guid = json_response["guid"]
        

    def multipart_upload(self,filename):
        session = boto3.Session()
        s3_client = session.client('s3',aws_access_key_id = aws_access_key, aws_secret_access_key = aws_secret_key)

        try:
            print("Uploading file: {}".format(filename))

            transfer_config = boto3.s3.transfer.TransferConfig(multipart_threshold=1024 * 25,max_concurrency=10,multipart_chunksize=1024 * 25,use_threads=True)
            transfer = boto3.s3.transfer.S3Transfer(client=s3_client, config=transfer_config)
            
            transfer.upload_file(filename, bucket_name, "latest.mp4", extra_args={"Metadata": {"metaguid": meta_guid}})
            

        except Exception as e:
            print("Error uploading: {}".format(e))

            

if __name__ == "__main__":
    upload_test = UPLOAD()
    upload_test.getSettings()
    upload_test.create_metadata()
    upload_test.multipart_upload("latest.mp4")
