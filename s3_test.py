import boto3
import os

endpoint_url= 'https://nrs.objectstore.gov.bc.ca' 

bucketname = os.environ['bucketname'] 

objid = os.environ['objid'] 

objkey =  os.environ['objkey'] 

s3_client = boto3.client('s3', endpoint_url=endpoint_url, aws_access_key_id=objid, aws_secret_access_key=objkey)
    
print(f'Here are the objects currently stored in {bucketname}:')

session = boto3.Session(aws_access_key_id=objid, aws_secret_access_key=objkey)

s3_resource = session.resource('s3', endpoint_url=endpoint_url)

my_bucket = s3_resource.Bucket(bucketname)

for my_bucket_object in my_bucket.objects.all():
    print(my_bucket_object.key)