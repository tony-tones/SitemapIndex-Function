import json
import boto3
import botocore
import os
from shutil import copyfileobj

def lambda_handler(event, context):
    s3          = boto3.resource('s3')
    bucket_name = os.environ['bucket']
    site_prefix = os.environ['site_prefix']
    bucket      = s3.Bucket(bucket_name)
    sitemap_f   = open('/tmp/sitemap.xml', 'a')
    index_f     = open('/tmp/index.html', 'a')
    json_f      = open('/tmp/objects.json', 'a')


    # does the bucket exist? -- complete
    def check_bucket(bucket):
        try:
            s3.meta.client.head_bucket(Bucket=bucket_name)
            print('Bucket Exists!')
            return True
        except botocore.exceptions.ClientError as e:
            # If a client error is thrown, then check that it was a 404 error.
            # If it was a 404 error, then the bucket does not exist.
            error_code = int(e.response['Error']['Code'])
            if error_code == 403:
                print('Private Bucket. Forbidden Access!')
                os._exit()
            elif error_code == 404:
                print('Bucket Does Not Exist!')
                os._exit()


    check_bucket(bucket)


    # if sitemap.xml is less than 5 min old, stop running -- coming soon


    # Download the bucket contents with boto3 -- complete
    client          = boto3.client('s3', region_name='us-east-1')
    paginator       = client.get_paginator('list_objects_v2')
    page_iterator   = paginator.paginate(Bucket=bucket_name)
    object_list     = []
    for page in page_iterator:
        for content in page['Contents']:
            content['LastModified'] = content['LastModified'].isoformat()
            object_list.append(content)
    json_f.write(json.dumps(object_list, indent=4))


    #remove sitemap.xml, index, and robots.txt -- coming soon


    # Add header to sitemap file -- complete
    sm_header = open('sitemap-header.txt', 'r')
    copyfileobj(sm_header, sitemap_f)
    sm_header.close()


    # Add header to index file -- complete
    idx_header = open('index-header.txt', 'r')
    copyfileobj(idx_header, index_f)
    idx_header.close()


    # loop stuff -- complete
    with open('/tmp/objects.json') as f:
        data = json.load(f)
        objects = data#['Contents']
        for object in objects:
            loc = '<loc>' + site_prefix + object['Key'] + '</loc>'
            mod = '<lastmod>' + object['LastModified'] + '</lastmod>'
            sitemap_f.writelines(['<url>\n','\t' + loc + '\n','\t' + mod + '\n','\t' + '<changefreq>monthly</changefreq>\n','\t' + '<priority>0.5</priority>\n','</url>\n'])
            fullline = '<a href=\"' + site_prefix + object['Key'] + '\">' + object['Key'] + '</a>'
            index_f.write(fullline + '\n')


    # Add Footer to the Index -- complete
    idx_footer = open('index-footer.txt', 'r')
    copyfileobj(idx_footer, index_f)
    idx_header.close()


    # Add Footer to the Sitemap -- complete
    sm_footer = open('sitemap-footer.txt', 'r')
    copyfileobj(sm_footer, sitemap_f)
    sm_header.close()


    # Close Files
    index_f.close()
    sitemap_f.close()
    json_f.close()


    # Upload completed Files -- complete
    s3.Object(bucket_name, 'sitemap.xml').upload_file('/tmp/sitemap.xml', ExtraArgs={'ContentType': 'application/xml'})
    s3.Object(bucket_name, 'index.html').upload_file('/tmp/index.html', ExtraArgs={'ContentType': 'text/html'})

    return 'Lambda Complete!'
