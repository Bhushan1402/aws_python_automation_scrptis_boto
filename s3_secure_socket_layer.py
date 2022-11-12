import boto3
import pandas as pd
import json

client = boto3.client('s3')
df = pd.read_csv("s3_buckets_name.csv", usecols=['bucket_name'])
count = 0

def get_policy(s3_bucket_arn):
    policy= { "Version": "2008-10-17", 
              "Statement": [ { "Effect": "Deny", 
                                "Principal": "*", 
                                "Action": 's3:*', 
                                "Resource": [s3_bucket_arn],
                                "Condition": { "Bool": { "aws:SecureTransport": "false"} } } ] }
    print(policy)
    return json.dumps(policy)

def updated_policy(s3_bucket_name):
    s3_client = boto3.client('s3')
    policy = s3_client.get_bucket_policy(Bucket=s3_bucket_name)
    updatedpolicy = json.loads(policy['Policy'])
    # print(updatedpolicy)
    user_policy = { "Effect": "Deny", "Principal": "*", "Action": 's3:*', "Resource": "arn:aws:s3:::"+s3_bucket_name+"/*","Condition": { "Bool": { "aws:SecureTransport": "false"} } }
    updatedpolicy['Statement'].append(user_policy) 
    # print(updatedpolicy)
    new_policy = json.dumps(updatedpolicy)
    return new_policy

def check_policy(s3_bucket_name):
    try:
        s3_policy = client.get_bucket_policy(
                Bucket=s3_bucket_name
            )
        # print(s3_policy)
        return 1
    except Exception as e:
        if "The bucket policy does not exist" in str(e):
            return 0
    
for s3_bucket_name in df['bucket_name']:
    s3_bucket_arn = "arn:aws:s3:::"+s3_bucket_name+"/*"
    return_from_check_policy = check_policy(s3_bucket_name)
    if return_from_check_policy == 1:
        print("updating policy")
        s3_pdated_policy = updated_policy(s3_bucket_name)
        print(s3_pdated_policy)
        response = client.put_bucket_policy(
                Bucket=s3_bucket_name,
                Policy=s3_pdated_policy
        )
        # print(response)
    else:
        response = client.put_bucket_policy(
                Bucket=s3_bucket_name,
                Policy=get_policy(s3_bucket_arn)
        )
        print(response)
