import json
import os
import sys

json_path = sys.argv[1]
alias = os.environ['ENV']
for root, subdir, files in os.walk(json_path):
  for fileName in files:
    if fileName == 'JavaChangeSetFile' or fileName == 'NodeChangeSetFile': 
      with open(fileName, 'r') as f:
          content = f.read()
          output = json.loads(content)
          for key in output:
              print 'Processing function: ' + output[key]
              arn = output[key]
              function_name = arn.split[':'][6]
              version = os.popen('aws lambda publish-version --function-name ' + function_name + ' --output text --query Version')
              alias_out = os.popen('aws lambda create-alias --function-name ' + function_name + ' --function-version ' + version + ' --name ' + alias)
              if 'ResourceConflictException' in alias_out:
                print 'Updating the alias: ' + alias + ' for lambda: ' + output[key]
                update_alias = os.popen('aws lambda update-alias --function-name ' + function_name + ' --function-version ' + version + ' --name ' + alias)
      f.close()