var AWS = require('aws-sdk');
var codeBuild = new AWS.CodeBuild();

exports.handler = (event, context, callback) => {
    console.log(event);
    const action = event.action;
    var pull_request = event.pull_request;
    var title = pull_request.title;
    var ticket = title.split(" ")[0];
    if (action == 'opened') {
        var param = {};
        param.projectName = 'projectw-node-lambda-build';
        param.artifactsOverride = { type: 'NO_ARTIFACTS' };
        param.environmentVariablesOverride = [];
        var envVariable = {};
        envVariable.name = 'JIRA_TICKET';
        envVariable.value = ticket;
        envVariable.type = 'PLAINTEXT';
        param.environmentVariablesOverride.push(envVariable);

        codeBuild.startBuild(param, function (err, data) {
            if (!err) {
                console.log(data);
                console.log("Successfully initiated the CodeBuild for PR: %s", title);
                callback(null, data)
            } else {
                console.error("Failed to initiate the build for PR %s", title, err);
                callback(err);
            }
        })
    } else {
        console.log("Not interested in PR state changes except Open");
        callback(null, "Un-interested state change for PR");
    }
};