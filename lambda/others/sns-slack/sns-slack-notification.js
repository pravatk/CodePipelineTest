var request = require('request');

var _convertSnsEventToSlackMessage = function (event) {
    var snsMessage = JSON.parse(event.Message);
    var slackMessage = {
        "channel": process.env.SLACK_CHANNEL,
        "username": snsMessage.sender,
        "text": "*" + snsMessage.subject + "*",
        "icon_emoji": ":aws:"
    }

    var color = "good";
    if (snsMessage.severity) {
        color = snsMessage.severity;
    }

    slackMessage.attachments = [
        {
            color: color,
            text: snsMessage.message
        }
    ];

    return slackMessage;
}

exports.handler = function (event, context, callback) {
    console.log("Got event", event);
    var slackMessage = _convertSnsEventToSlackMessage(event.Records[0].Sns);
    console.log("Sending slack message:", slackMessage);
    request({
        url: process.env.SLACK_WEBHOOK_URL,
        method: 'POST',
        body: JSON.stringify(slackMessage),
        headers: {
            'Content-Type': 'application/json'
        }
    }, function (err, response, body) {
        if (err) {
            console.log("Error in sending notificaiton to slack", err);
            callback(err);
        } else {
            callback(null);
        }
    });
}