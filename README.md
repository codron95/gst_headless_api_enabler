## GST Enable API access Automation
Runs a headless browser service to automate enabling the API access for GST Portal

### Modules
* Web Service
  * Takes the responsibility of being the communication medium to the outside world.
  * Exposes end points for fetching captcha and enabling API access.
  * Stores and retrieves browser sessions stored in persistent memory store as required.
  * Terminates the browser session post the enable API call.
* Memory Corrector
  * Take the responsibility of clearing stale tokens from persistent store.
  
  
### Architecture
![](https://ibin.co/4ijffLZq25NC.png)

### API Docs

* GET /captcha/

##### Response
* code: 200
```
{
  "message": "Token generated",
  "errors": [],
  "data":{
    "captcha_base64": <base64 string>,
    "token": <browser session id>,
    "ts": <timestamp>
   }
}
```


* PUT /enable_api/<token>

##### Request Data
```
{
  "username": <username>,
  "password": <password>,
  "captcha": <captcha>
}
```

##### Response
* code: 200 
```
{
  "message": "API access enabled",
  "errors": [],
  "data": {
    "token": <browser session id>
   }
}
```

* code: 404
```
{
  "message": "Token not found",
  "errors": ["Token not found"],
  "data": {
    "token": <browser session id>
  }
}
```

* code: 400
```
{
  "message": "Login Unsuccessful",
  "errors": [<reason for login failure [captcha, username or password incorrect]>],
  "data": {
    "token": <browser session id>
  }
}
```

* code: 500
```
{
  "message": "There was an unexpected error. Please try again later.",
  "errors": ["There was an unexpected error. Please try again later."],
  "data": {
    "token": <browser session id>
  }
}
```
