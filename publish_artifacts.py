import json
import os
import sys
import subprocess

if 'ENV' in os.environ:
  alias = os.environ['ENV']
  print 'Alias: ' + alias
else:
    print 'Environment is missing! Pass the publish alias details as environment variable'
    exit()
os.system('aws lambda list-functions --query Functions > tmpJson.json')
with open('tmpJson.json') as f:
  all_function = f.read()
  fun_json = json.loads(all_function)
  for fun_details in fun_json:
    if 'projectw' in fun_details['FunctionName']:
      print 'Processing function: ' + fun_details['FunctionName']
      function_name = fun_details['FunctionName']
      cmd = 'aws lambda publish-version --function-name ' + function_name
      process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=None, shell=True)
      ver = process.communicate()
      version_json = json.loads(ver[0])

      cmd = 'aws lambda create-alias --function-name ' + function_name + ' --function-version ' + version_json['Version'] + ' --name ' + alias + ' --query AliasArn'
      print cmd
      process = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True, stderr=subprocess.STDOUT)
      alias_str = process.communicate()
      if alias_str[0].find('ResourceConflictException') != -1:
        print 'Updating the alias: ' + alias + ' for lambda: ' + function_name
        cmd = 'aws lambda update-alias --function-name ' + function_name + ' --function-version ' + version_json['Version'] + ' --name ' + alias
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True, stderr=None)
        update_alias = process.communicate()
        print update_alias[0]
  f.close()