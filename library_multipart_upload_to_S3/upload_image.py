import datetime
import configparser
import json
import time
import requests
import boto3

config = configparser.ConfigParser()
config.read('../configs/library_multipart_upload_to_S3/config.ini')

bucket_name = ""
current_date = datetime.datetime.now()
post_data = {
  "meta": {
    "type": "image",
    "title": "Python_Upload_{}".format(current_date),
    "customMeta01": "customMetaData01",
    "customMeta02": "customMetaData02",
    "customMeta03": "customMetaData03",
    "customMeta04": "customMetaData04"
  }
}
meta_guid = ""

class UPLOAD:

    def __init__(self):
        self.config = config
        self.get_config_stuff()

    def get_config_stuff(self):
        global base_image_url
        global api_key_images
        global multipart_upload_image
        global create_image_metadata
        global list_all_images
        global aws_access_key
        global aws_secret_key

        if config.has_section('endpoints'):
            base_image_url = config.get('endpoints','base_image_url')
            multipart_upload_image = config.get('endpoints','multipart_upload_image')
            create_image_metadata = config.get('endpoints','create_image_metadata')
            list_all_images = config.get('endpoints','list_all_images')
        else:
            print("There is no endpoints section or there is a missing endpoint the config file.\n")
            exit()

        if config.has_option('credentials','api_key_images'):
            api_key_images = config.get('credentials','api_key_images')
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
        headers = {'accept':'application/json', 'x-api-key': api_key_images}
        full_url = base_image_url + multipart_upload_image
        response = requests.get(full_url, headers=headers)
        bucket_name = json.loads(response.text)["data"]["bucket"]


    def create_metadata(self):
        print("Creating Metadata...")
        global meta_guid
        headers = {'Content-Type':'application/json', 'Accept':'application/json', 'x-api-key': api_key_images}
        full_url = base_image_url + create_image_metadata
        response = requests.post(full_url, json=post_data, headers=headers)
        json_response = json.loads(response.text)
        meta_guid = json_response["guid"]
        

    def multipart_upload(self, filename):
        session = boto3.Session()
        s3_client = session.client("s3",aws_access_key_id=aws_access_key, aws_secret_access_key=aws_secret_key)

        try:
            print("Uploading file: {}".format(filename))

            transfer_config = boto3.s3.transfer.TransferConfig(multipart_threshold=1024 * 25,max_concurrency=10,multipart_chunksize=1024 * 25,use_threads=True)
            transfer = boto3.s3.transfer.S3Transfer(client=s3_client, config=transfer_config)
            
            transfer.upload_file(filename, bucket_name, filename, extra_args={"Metadata": {"metaguid": meta_guid}})
            
        except Exception as err:
            print("Error uploading: {}".format(err))


    def checkup_metadata_for_image(self):
        time.sleep(5)
        global post_data
        print("Listing the uploaded image with all its metadata...")
        full_url = base_image_url + list_all_images
        headers = {'Content-Type':'application/json', 'Accept':'application/json', 'x-api-key': api_key_images}
        response = requests.get(full_url, headers=headers)
        json_response = json.loads(response.text)
        for i in range(0,len(json_response['data'])):
                if 'title' not in json_response['data'][i]['meta']:
                    continue
                else:
                    if post_data['meta']['title'] == json_response['data'][i]['meta']['title']:
                        print(json.dumps(json_response['data'][i], indent=2))





if __name__ == "__main__":
    upload_test = UPLOAD()
    upload_test.getSettings()
    upload_test.create_metadata()
    upload_test.multipart_upload("image.jpg")
    upload_test.checkup_metadata_for_image()
