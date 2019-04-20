import glob
import os

import boto3

def upload(fig_dir, bucket_name, bucket_dir):
    url_list = []
    figpath_list = glob.glob(fig_dir+"/*")
    for figpath in figpath_list:
        if figpath.find('png') > -1:
            fig = open(figpath, 'rb')
            fig_name = (figpath.strip(fig_dir)).strip('\\')
            s3_client = boto3.client(service_name = 's3',
                                     aws_access_key_id = os.environ['AWS_ACCESS'],
                                     aws_secret_access_key = os.environ['AWS_SECRET_ACCESS'],
                                     region_name = os.environ['REGION_NAME']
                                     )
            result  = s3_client.put_object(Bucket=bucket_name, Key=(bucket_dir+"/"+fig_name), Body=fig)
            fig_url = s3_client.generate_presigned_url(ClientMethod = 'get_object',
                                                     Params = {'Bucket': bucket_name, 'Key':(bucket_dir+'/'+fig_name) }, 
                                                     ExpiresIn = 1000,
                                                     HttpMethod = 'GET'
                                                     )
            url_list.append(fig_url)

    return url_list

def exists(bucket_name, bucket_dir):
    content_list = []

    s3_client = boto3.client(service_name = 's3',
                             aws_access_key_id = os.environ['AWS_ACCESS'],
                             aws_secret_access_key = os.environ['AWS_SECRET_ACCESS'],
                             region_name = os.environ['REGION_NAME']
                             )
    response = s3_client.list_objects(Bucket=bucket_name, Prefix='')
    if 'Contents' in response:
        keys = [content['Key'] for content in response['Contents']]
        for key in keys:
            if key.find(bucket_dir) > -1:
                fig_url = s3_client.generate_presigned_url(ClientMethod = 'get_object',
                                         Params = {'Bucket': bucket_name, 'Key':key }, 
                                         ExpiresIn = 1000,
                                         HttpMethod = 'GET'
                                         )
                content_list.append(fig_url)
    else:
        print("No Contents in " + bucket_name)
        
    return content_list

if __name__ == '__main__':
    FIG_DIR = './tmp/6550'
    BUCKET_NAME = 'kabu-tool'
    KEY = '6550'

    url_list = exists(BUCKET_NAME, KEY)
    if url_list == []:
        url_list = upload(FIG_DIR, BUCKET_NAME, KEY)
    print(url_list)
        