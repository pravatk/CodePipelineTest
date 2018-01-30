import json
import os
import sys
import subprocess

if 'ENV' in os.environ:
  alias = os.environ['ENV']
  print 'Alias: ' + alias
else:
    print 'Environment is missing! Pass the environment name to the build which would be used for creating the alias'
    exit()
if 'IS_VERSION' in os.environ:
  is_version = os.environ['IS_VERSION'] == 'true'
else:
  is_version = False

if 'CodePipelineJobId' in os.environ:
  job_id = os.environ['CodePipelineJobId']
# Runs the list-functions aws cli command to fetch all available lambdas
os.system('aws lambda list-functions --query Functions > tmpJson.json')
with open('tmpJson.json') as f:
  all_function = f.read()
  fun_json = json.loads(all_function)
  for fun_details in fun_json:
    # For all function starting with projectw, publish a version and create/update the alias with the same details
    if 'projectw' in fun_details['FunctionName']:
      print 'Processing function: ' + fun_details['FunctionName']
      function_name = fun_details['FunctionName']
      if is_version == True:
        cmd = 'aws lambda publish-version --function-name ' + function_name
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=None, shell=True)
        ver = process.communicate()
        version_json = json.loads(ver[0])
        version = version_json['Version']
      else:
        version = '$LATEST'
      print 'Updating the alias: ' + alias + ' for lambda: ' + function_name
      cmd = 'aws lambda update-alias --function-name ' + function_name + ' --function-version ' + version + ' --name ' + alias
      process = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True, stderr=None)
      update_alias = process.communicate()
      print update_alias[0]
      if update_alias[0].find('ResourceNotFoundException') != -1:
        print 'Creating the alias: ' + alias + ' for function: ' + function_name
        cmd = 'aws lambda create-alias --function-name ' + function_name + ' --function-version ' + version_json['Version'] + ' --name ' + alias + ' --query AliasArn'
        print cmd
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True, stderr=subprocess.STDOUT)
        alias_str = process.communicate()
  f.close()
  os.system('aws put-job-success-result --job-id ' + job_id)