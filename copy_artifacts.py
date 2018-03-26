import json
import os
import sys
import subprocess
import boto3
import time

target_bucket = os.environ['DESTINATION_BUCKET']

sts_client = boto3.client('sts')
assumedRoleObject = sts_client.assume_role(
    RoleArn=os.environ['ASSUME_ROLE_ARN'],
    RoleSessionName="AssumeRoleSession1"
)
try:
    print 'Assume role successful' + json.dumps(json.loads(assumedRoleObject))
except Exception as e:
    print(e.message)
    print e

credentials = assumedRoleObject['Credentials']

s3 = boto3.client(
    's3',
    aws_access_key_id=credentials['AccessKeyId'],
    aws_secret_access_key=credentials['SecretAccessKey'],
    aws_session_token=credentials['SessionToken']
)
# Iterate over all json files under statemachines folder and for each json, create a state machine.
# This script expects STEP_FUNCTION_ROLE_ARN as environment variables
folder = str(time.time())
artifact_folder = folder + '/' + 'artifacts'
template_folder = folder + '/' + 'templates'
for root, subdir, files in os.walk('.'):
    for fileName in files:
        file_path = os.path.join(root, fileName)
        if fileName.endswith(".zip") or fileName.endswith('.json'):
            print 'Uploading ' + fileName + ' from ' + file_path
            if fileName.endswith(".zip"):
                object_key = artifact_folder + '/' + fileName
            else:
                object_key = template_folder + '/' + fileName
            with open(file_path, 'rb') as f:
                response = s3.put_object(
                    Body=f.read(),
                    Bucket=target_bucket,
                    Key=object_key,
                    ServerSideEncryption='AES256'
                )
                print 'File putObject respone ' + json.dumps(response)
            f.close()
        else:
            print 'Not interested file ' + file_path
with open('samTemplate_node.yaml') as template:
    lines = template.readlines()
    with open('output_template.yaml', 'w') as output:
        for line in lines:
            if line.find('CodeUri') != -1:
                x = line.split('/')
                file_name = x[len(x) - 1]
                code = 'CodeUri: s3://' + target_bucket + \
                    '/' + artifact_folder + '/' + file_name
                output.write(code)
            else:
                output.write(line)
    output.close()
template.close()
with open('output_template.yaml', 'r') as output:
    response = s3.put_object(
        Body=output.read(),
        Bucket=target_bucket,
        Key=template_folder + '/' + fileName,
        ServerSideEncryption='AES256'
    )
output.close()
