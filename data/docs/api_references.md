# Notify a single user

POST https://api.fyno.io/v1/{WSID}/{version}/event
Content-Type: application/json

This API enables you to fire a notification event, which sends out notifications to your users. <br/><br/>Before firing your first notification event, you must perform the following actions in your Fyno account:<br/>- Create a Template<br/>- Create a Notification Event<br/>- Create an API Key<br/>- And obtain your workspace ID from the API Keys page.

Reference: https://fyno.io/docs/api-reference/notify-a-single-user

## OpenAPI Specification

```yaml
openapi: 3.1.0
info:
  title: Fyno Rest API
  version: 1.0.0
paths:
  /{WSID}/{version}/event:
    post:
      operationId: notify-a-single-user
      summary: Notify a single user
      description: >-
        This API enables you to fire a notification event, which sends out
        notifications to your users. <br/><br/>Before firing your first
        notification event, you must perform the following actions in your Fyno
        account:<br/>- Create a Template<br/>- Create a Notification Event<br/>-
        Create an API Key<br/>- And obtain your workspace ID from the API Keys
        page.
      tags:
        - subpackage_fireAnEvent
      parameters:
        - name: WSID
          in: path
          description: >-
            Enter your workspace ID. You can obtain this value from the API Keys
            page within your Fyno account.
          required: true
          schema:
            type: string
        - name: version
          in: path
          description: Enter the version for which you wish to fire the notification.
          required: true
          schema:
            $ref: '#/components/schemas/WsidVersionEventPostParametersVersion'
        - name: Authorization
          in: header
          description: >-
            Enter your API Key. If you don't have it already, you can create one
            from the API Keys page within your Fyno account
          required: true
          schema:
            type: string
      responses:
        '202':
          description: >-
            Request accepted successfully and it will be processed
            asynchronously.
          content:
            application/json:
              schema:
                $ref: >-
                  #/components/schemas/Fire an
                  Event_notifyASingleUser_Response_202
        '400':
          description: Event name does not exist
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/NotifyASingleUserRequestBadRequestError'
        '401':
          description: API Key or Workspace ID is invalid. User is unauthorised.
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/NotifyASingleUserRequestUnauthorizedError'
      requestBody:
        description: >-
          Your event payload must specify at least *`distinct_id`* or *`to`*
          while firing a notification event.<br/><br/>If the payload
          contains&#58;<br/><br/>- <b>Option 1&#58;</b> ONLY *`to`* (and no
          *`distinct_id`*) - the notification event uses all destination values
          from the *`to`* object (as it is).<br/><br/>- <b>Option 2&#58;</b>
          ONLY *`distinct_id`* (and no *`to`*) - the notificaton event uses all
          destination values (such as SMS, WhatsApp, Email, Push, Voice and so
          on) from the user's profile and sends the notification.<br/><br/>-
          <b>Option 3&#58;</b> BOTH *`distinct_id`* and *`to`* - the `to` and
          `distinct_id` channel data merges (`to` object take precedences) and
          sends the notification. The sent notification is tagged to the ID
          specified, which can be then used to search the logs by using
          `distinct_id`.
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/version_event_body'
servers:
  - url: https://api.fyno.io/v1
    description: https://api.fyno.io/v1
components:
  schemas:
    WsidVersionEventPostParametersVersion:
      type: string
      enum:
        - live
        - test
      default: live
      title: WsidVersionEventPostParametersVersion
    CallbackAllowlistUrl:
      oneOf:
        - type: string
        - type: array
          items:
            type: string
      description: >-
        (Optional) Allowlist URL name where you want to receive delivery
        reports. Can be array of Allowlist URL names too if you want the
        delivery reports in multiple URLs. If `allowlist_url` is not specified,
        but callback object has `enable=true` and `custom_id` is specified, then
        the delivery reports will be sent to the default endpoint set to receive
        delivery reports in the [Configuring Allowlist
        URL](../../configuring-allowlist-url-sqs-to-receive-delivery-report)
        settings.
      title: CallbackAllowlistUrl
    callback:
      type: object
      properties:
        custom_id:
          type: string
          description: >-
            Use this parameter to send an ID that you would want to receive as a
            response (for reconciliation) in your delivery callback.
        custom1:
          type: string
          description: >-
            (Optional) Use this parameter to send another ID that you want to
            receive as a response (for reconciliation) in your delivery
            callback.
        custom2:
          type: string
          description: >-
            (Optional) Use this parameter to send yet another ID that you want
            to receive as a response (for reconciliation) in your delivery
            callback.
        custom3:
          type: string
          description: >-
            (Optional) Use this parameter to send yet another ID that you want
            to receive as a response (for reconciliation) in your delivery
            callback.
        enable:
          type: boolean
          description: >-
            (Optional) Set `true` to enable delivery callback or `false` to
            disable delivery callback. The default value is `true` if
            `custom_id` is specified.
        allowlist_url:
          $ref: '#/components/schemas/CallbackAllowlistUrl'
          description: >-
            (Optional) Allowlist URL name where you want to receive delivery
            reports. Can be array of Allowlist URL names too if you want the
            delivery reports in multiple URLs. If `allowlist_url` is not
            specified, but callback object has `enable=true` and `custom_id` is
            specified, then the delivery reports will be sent to the default
            endpoint set to receive delivery reports in the [Configuring
            Allowlist
            URL](../../configuring-allowlist-url-sqs-to-receive-delivery-report)
            settings.
      required:
        - custom_id
      description: >-
        (Optional) You can enable callback for an event by specifying the
        `callback` attribute in the payload of the event. By enabling callback,
        you will be able to receive delivery status of the events onto your
        webhook URL specified in the "Allowlist URL" section of the application.
        See [Configuring Allowlist URL/SQS to receive Delivery
        Report](../../configuring-allowlist-url-sqs-to-receive-delivery-report)
        for more details.
      title: callback
    data:
      type: object
      properties: {}
      description: >-
        (Optional) Enter the keys and values of your replaceabale placeholders.
        These values are replaced in the respective keys of the template when
        the notification is sent.
      title: data
    event:
      type: string
      description: Enter the name of the event you wish to fire.
      title: event
    to:
      type: object
      properties:
        discord:
          type: string
          description: Enter the discord ID of the user.
        email:
          type: string
          description: Enter the email address of the user.
        inapp:
          type: string
          description: Enter the distinct ID or the generated token of the user.
        push:
          type: string
          description: >-
            If you use multiple Push providers, add the following prefix for the
            respective provider tokens:<br/><br/>- <b>For Expo&#58;</b>
            `expo_token:`<your_pushtoken><br/>- <b>For FCM&#58;</b>
            `fcm_token:`<your_pushtoken><br/>- <b>For OneSignal
            playerId&#58;</b> `onesignal_player_id:`<enter_playerid><br/>-
            <b>For OneSignal externalId&#58;</b>
            `onesignal_external_id:`<enter_externalid><br/>- <b>For Mi
            Push&#58;</b> `mi_token:`<your_pushtoken><br/><br/>If you use just
            one provider, then the prefix is not required. However, if you wish
            to use OneSignal with playerId token, then the prefix is required.
        slack:
          type: string
          description: Enter the channel ID, user ID, or email address of the user.
        sms:
          type: string
          description: >-
            Enter the mobile number of the user. The number must start with the
            country code (preferably in E.164 format). For example&#58;
            +919879XXXXXX.
        teams:
          type: string
          description: >-
            Enter the channel name. For teams, we currently support sending to
            one channel only. To send to multiple channels, do get in touch and
            we can share a workaround.
        voice:
          type: string
          description: >-
            Enter the mobile number of the user. The number must start with the
            country code (preferably in E.164 format). For example&#58;
            +919879XXXXXX.
        whatsapp:
          type: string
          description: >-
            Enter the WhatsApp mobile number of the user. The number must start
            with the country code (preferably in E.164 format). For example&#58;
            +919879XXXXXX
      title: to
    VersionEventBody0:
      type: object
      properties:
        callback:
          $ref: '#/components/schemas/callback'
        data:
          $ref: '#/components/schemas/data'
        event:
          $ref: '#/components/schemas/event'
        to:
          $ref: '#/components/schemas/to'
      required:
        - event
        - to
      title: VersionEventBody0
    distinct_id:
      type: string
      description: Enter the distinct ID that you use to identify the recipient.
      title: distinct_id
    VersionEventBody1:
      type: object
      properties:
        callback:
          $ref: '#/components/schemas/callback'
        data:
          $ref: '#/components/schemas/data'
        distinct_id:
          $ref: '#/components/schemas/distinct_id'
        event:
          $ref: '#/components/schemas/event'
      required:
        - distinct_id
        - event
      title: VersionEventBody1
    VersionEventBody2:
      type: object
      properties:
        callback:
          $ref: '#/components/schemas/callback'
        data:
          $ref: '#/components/schemas/data'
        distinct_id:
          $ref: '#/components/schemas/distinct_id'
        event:
          $ref: '#/components/schemas/event'
        to:
          $ref: '#/components/schemas/to'
      required:
        - distinct_id
        - event
        - to
      title: VersionEventBody2
    version_event_body:
      oneOf:
        - $ref: '#/components/schemas/VersionEventBody0'
        - $ref: '#/components/schemas/VersionEventBody1'
        - $ref: '#/components/schemas/VersionEventBody2'
      title: version_event_body
    inline_response_202_response_discord:
      type: object
      properties:
        destination:
          type: string
        msg_id:
          type: string
        status:
          type: string
      required:
        - destination
        - msg_id
        - status
      title: inline_response_202_response_discord
    inline_response_202_response_email:
      type: object
      properties:
        destination:
          type: string
        msg_id:
          type: string
        status:
          type: string
      required:
        - destination
        - msg_id
        - status
      title: inline_response_202_response_email
    inline_response_202_response_inapp:
      type: object
      properties:
        destination:
          type: string
        msg_id:
          type: string
        status:
          type: string
      required:
        - destination
        - msg_id
        - status
      title: inline_response_202_response_inapp
    inline_response_202_response_push:
      type: object
      properties:
        destination:
          type: string
        msg_id:
          type: string
        status:
          type: string
      required:
        - destination
        - msg_id
        - status
      title: inline_response_202_response_push
    inline_response_202_response_slack:
      type: object
      properties:
        destination:
          type: string
        msg_id:
          type: string
        status:
          type: string
      required:
        - destination
        - msg_id
        - status
      title: inline_response_202_response_slack
    inline_response_202_response_sms:
      type: object
      properties:
        destination:
          type: string
        msg_id:
          type: string
        status:
          type: string
      required:
        - destination
        - msg_id
        - status
      title: inline_response_202_response_sms
    inline_response_202_response_teams:
      type: object
      properties:
        destination:
          type: string
        msg_id:
          type: string
        status:
          type: string
      required:
        - destination
        - msg_id
        - status
      title: inline_response_202_response_teams
    inline_response_202_response:
      type: object
      properties:
        discord:
          $ref: '#/components/schemas/inline_response_202_response_discord'
        email:
          $ref: '#/components/schemas/inline_response_202_response_email'
        inapp:
          $ref: '#/components/schemas/inline_response_202_response_inapp'
        push:
          $ref: '#/components/schemas/inline_response_202_response_push'
        slack:
          $ref: '#/components/schemas/inline_response_202_response_slack'
        sms:
          $ref: '#/components/schemas/inline_response_202_response_sms'
        teams:
          $ref: '#/components/schemas/inline_response_202_response_teams'
        voice:
          $ref: '#/components/schemas/inline_response_202_response_sms'
        whatsapp:
          $ref: '#/components/schemas/inline_response_202_response_sms'
      title: inline_response_202_response
    Fire an Event_notifyASingleUser_Response_202:
      type: object
      properties:
        event:
          type: string
        received_time:
          type: string
          format: date
        request_id:
          type: string
        response:
          $ref: '#/components/schemas/inline_response_202_response'
      required:
        - event
        - received_time
        - request_id
        - response
      title: Fire an Event_notifyASingleUser_Response_202
    NotifyASingleUserRequestBadRequestError:
      type: object
      properties:
        _message:
          type: string
        status:
          type: string
      required:
        - _message
        - status
      title: NotifyASingleUserRequestBadRequestError
    NotifyASingleUserRequestUnauthorizedError:
      type: object
      properties:
        _message:
          type: string
        status:
          type: string
      required:
        - _message
        - status
      title: NotifyASingleUserRequestUnauthorizedError
  securitySchemes:
    BearerAuth:
      type: http
      scheme: bearer
      description: >-
        Enter your API Key. If you don't have it already, you can create one
        from the API Keys page within your Fyno account

```

## Examples



**Request**

```json
{
  "event": "event_name"
}
```

**Response**

```json
{
  "event": "event_name",
  "received_time": "2025-02-17T07:49:13.352Z",
  "request_id": "XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX",
  "response": {
    "discord": {
      "destination": "101XXXXXXXXXX7XXXXX",
      "msg_id": "XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX:XXXX",
      "status": "ok"
    },
    "email": {
      "destination": "abcde@fghi.com",
      "msg_id": "XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX:XXXX",
      "status": "ok"
    },
    "inapp": {
      "destination": "12345",
      "msg_id": "XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX:XXXX",
      "status": "ok"
    },
    "push": {
      "destination": "ExponentPushToken[XXXXX]",
      "msg_id": "XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX:XXXX",
      "status": "ok"
    },
    "slack": {
      "destination": "CXXXXXXXXXX",
      "msg_id": "XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX:XXXX",
      "status": "ok"
    },
    "sms": {
      "destination": "+919879XXXXXX",
      "msg_id": "XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX:XXXX",
      "status": "ok"
    },
    "teams": {
      "destination": "General",
      "msg_id": "XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX:XXXX",
      "status": "ok"
    },
    "voice": {
      "destination": "+919879XXXXXX",
      "msg_id": "XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX:XXXX",
      "status": "ok"
    },
    "whatsapp": {
      "destination": "+919879XXXXXX",
      "msg_id": "XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX:XXXX",
      "status": "ok"
    }
  }
}
```

**SDK Code**

```python
import requests

url = "https://api.fyno.io/v1/FYXXXXXXXX/live/event"

payload = { "event": "event_name" }
headers = {
    "Authorization": "Bearer <apiKey>",
    "Content-Type": "application/json"
}

response = requests.post(url, json=payload, headers=headers)

print(response.json())
```

```javascript
const url = 'https://api.fyno.io/v1/FYXXXXXXXX/live/event';
const options = {
  method: 'POST',
  headers: {Authorization: 'Bearer <apiKey>', 'Content-Type': 'application/json'},
  body: '{"event":"event_name"}'
};

try {
  const response = await fetch(url, options);
  const data = await response.json();
  console.log(data);
} catch (error) {
  console.error(error);
}
```

```go
package main

import (
	"fmt"
	"strings"
	"net/http"
	"io"
)

func main() {

	url := "https://api.fyno.io/v1/FYXXXXXXXX/live/event"

	payload := strings.NewReader("{\n  \"event\": \"event_name\"\n}")

	req, _ := http.NewRequest("POST", url, payload)

	req.Header.Add("Authorization", "Bearer <apiKey>")
	req.Header.Add("Content-Type", "application/json")

	res, _ := http.DefaultClient.Do(req)

	defer res.Body.Close()
	body, _ := io.ReadAll(res.Body)

	fmt.Println(res)
	fmt.Println(string(body))

}
```

```ruby
require 'uri'
require 'net/http'

url = URI("https://api.fyno.io/v1/FYXXXXXXXX/live/event")

http = Net::HTTP.new(url.host, url.port)
http.use_ssl = true

request = Net::HTTP::Post.new(url)
request["Authorization"] = 'Bearer <apiKey>'
request["Content-Type"] = 'application/json'
request.body = "{\n  \"event\": \"event_name\"\n}"

response = http.request(request)
puts response.read_body
```

```java
import com.mashape.unirest.http.HttpResponse;
import com.mashape.unirest.http.Unirest;

HttpResponse<String> response = Unirest.post("https://api.fyno.io/v1/FYXXXXXXXX/live/event")
  .header("Authorization", "Bearer <apiKey>")
  .header("Content-Type", "application/json")
  .body("{\n  \"event\": \"event_name\"\n}")
  .asString();
```

```php
<?php
require_once('vendor/autoload.php');

$client = new \GuzzleHttp\Client();

$response = $client->request('POST', 'https://api.fyno.io/v1/FYXXXXXXXX/live/event', [
  'body' => '{
  "event": "event_name"
}',
  'headers' => [
    'Authorization' => 'Bearer <apiKey>',
    'Content-Type' => 'application/json',
  ],
]);

echo $response->getBody();
```

```csharp
using RestSharp;

var client = new RestClient("https://api.fyno.io/v1/FYXXXXXXXX/live/event");
var request = new RestRequest(Method.POST);
request.AddHeader("Authorization", "Bearer <apiKey>");
request.AddHeader("Content-Type", "application/json");
request.AddParameter("application/json", "{\n  \"event\": \"event_name\"\n}", ParameterType.RequestBody);
IRestResponse response = client.Execute(request);
```

```swift
import Foundation

let headers = [
  "Authorization": "Bearer <apiKey>",
  "Content-Type": "application/json"
]
let parameters = ["event": "event_name"] as [String : Any]

let postData = JSONSerialization.data(withJSONObject: parameters, options: [])

let request = NSMutableURLRequest(url: NSURL(string: "https://api.fyno.io/v1/FYXXXXXXXX/live/event")! as URL,
                                        cachePolicy: .useProtocolCachePolicy,
                                    timeoutInterval: 10.0)
request.httpMethod = "POST"
request.allHTTPHeaderFields = headers
request.httpBody = postData as Data

let session = URLSession.shared
let dataTask = session.dataTask(with: request as URLRequest, completionHandler: { (data, response, error) -> Void in
  if (error != nil) {
    print(error as Any)
  } else {
    let httpResponse = response as? HTTPURLResponse
    print(httpResponse)
  }
})

dataTask.resume()
```