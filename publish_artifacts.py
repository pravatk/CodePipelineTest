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
  print 'Job ID: ' + job_id
# Runs the list-functions aws cli command to fetch all available lambdas
process = subprocess.Popen('aws lambda list-functions --query Functions > tmpJson.json',stdout=subprocess.PIPE, stderr=None, shell=True)
res = process.communicate()
print 'List functions output: ' + res[0]

with open('tmpJson.json') as f:
  all_function = f.read()
  fun_json = json.loads(all_function)
  for fun_details in fun_json:
    # For all function starting with projectw, publish a version and create/update the alias with the same details
    if 'projectw' in fun_details['FunctionName']:
      print 'Processing function: ' + fun_details['FunctionName']
      function_name = fun_details['FunctionName']
      if is_version:
        cmd = 'aws lambda publish-version --function-name ' + function_name
        try:
          proc = subprocess.check_output(cmd)
          print proc
          ver_json = json.loads(proc)
          version = ver_json['Version']
        except subprocess.CalledProcessError as err:
          print err.returncode
          print err.message
      else:
        print 'Marking the version as $LATEST'
        version = '$LATEST'
      
      print 'Updating the alias: ' + alias + ' for lambda: ' + function_name
      cmd = 'aws lambda update-alias --function-name ' + function_name + ' --function-version ' + version + ' --name ' + alias
      try:
          proc = subprocess.check_output(cmd)
          print proc
      except subprocess.CalledProcessError as err:
        print err.returncode
        print err.message
        print 'Creating the alias: ' + alias + ' for function: ' + function_name
        cmd = 'aws lambda create-alias --function-name ' + function_name + ' --function-version ' + version + ' --name ' + alias + ' --query AliasArn'
        try:
          proc = subprocess.check_output(cmd)
          print proc
        except subprocess.CalledProcessError as inner_err:
          print inner_err.message
f.close()
cmd = 'aws codepipeline put-job-success-result --job-id ' + job_id
try:
  proc = subprocess.check_output(cmd)
  print proc
except subprocess.CalledProcessError as err:
  print err.returncode
  print err.message