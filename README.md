# Monitor Assets

In this repo, I’ll show you how to create a **Monitor** that keep an eye on your **website** and it **assets**.<br>
We will be using Python3.7 + Serverless lambda

## Getting Started

In order to go through this tutorial, make sure you have:
* Installed Python 3.7.
* Installed Node.js v6.5.0 or later.
* AWS account with admin rights (You can create one for free [right here](https://portal.aws.amazon.com/gp/aws/developer/registration/index.html)).

## Here is the plan

1. Setup Serverless framework
1. Get AWS credentials
1. Write backend of the Assets Monitor with python3.7
1. Deploy backend to Lambda
1. Schedule running



## Step 1: Serverless framework

Let’s start from the beginning.
<br>In order to easily write and deploy our lambda we will use this awesome framework called [Serverless](https://serverless.com/). 
<br>It’s written on NodeJS so we need npm to install it.
<br>Let’s go:

```javascript
npm install -g serverless
```
After this, let’s create a new project from template:

```javascript
serverless create --template aws-python3 --path my-assets-monitor
```
It will create a new folder my-assets-monitor with two files:
1. handler.py  — a template for your Python code
1. serverless.yml — configuration file

## Step 2: AWS Credentials

This is the best part of this process, because once you’ve got credentials,
<br> you’ll never deal with AWS again. 
<br>It’s super easy:

1. Log in to your AWS Console, go to [My Security Credentials > User](https://console.aws.amazon.com/iam/home#/users) and click on “Add User” blue button.
1. Specify username (something like “serverless-admin”) and choose only “Programmatic access” checkbox.
1. On the second page, choose “Attach existing policies directly” and look for “Administrator Access”.
1. Once you created the user, copy your “Access key ID” and “Secret access key”. 
1. This is what you actually need to continue.
(Tip: Save them where you can find them ;) )

Congrats. You’ve got your keys. Open your terminal in and execute:

```javascript
serverless config credentials --provider aws --key xxxxxxxxxxxxxx --secret xxxxxxxxxxxxxx
```

## Step 3: Write Assets Monitor Code

I’m not going to teach you how to write in Python, so just copy the code and paste to your `handler.py` file:

[handler.py source code](https://raw.githubusercontent.com/uriafranko/Monitor-Assests/master/handler.py)

Now create new file in the same directory and call it mailer.py,<br>
Copy this code and paste it in:

[mailer.py source code](https://raw.githubusercontent.com/uriafranko/Monitor-Assests/master/mailer.py)

If you are lazy enough, just fork or clone it from the repository.<br>

Also, you will need to create `requirements.txt` file and write:
```
requests
bs4
```
and execute this command to install the packages locally:
```text
pip install -r requirements.txt -t vendored
```

## Step 4: Deploy to AWS Lambda

Pretty much like on Heroku, all you need is one configuration file “serverless.yml”.<br> 
Go ahead and edit yours to make it look like this:
```yaml
service: my-asset-monitor

provider:
  name: aws
  runtime: python3.7
  stage: dev
  region: us-east-1
  environment:
    AWS_KEY: ""
    AWS_SECRET: ""
    TARGET_URL: ""
    SOURCE_EMAIL: ""
    DESTINATION_EMAIL: ""
  memorySize: 256


functions:
  post:
    handler: handler.main
    events:
      - schedule:
          name: asset-checker-schedule
          description: 'Schedule asset checking every 30 minutes'
          rate: rate(30 minutes)
```
#### Notice that you need to change
* **AWS_KEY** -> Your AWS key that we created
* **AWS_SECRET** -> Your AWS key that we created
* **TARGET_URL** -> The website that you want to monitor (Ex: 'https://google.com')
* **SOURCE_EMAIL** -> Your verified email that you can get/verify [here](https://console.aws.amazon.com/ses/home?region=us-east-1#verified-senders-email:)
* **DESTINATION_URL** -> The email that the notifications will be sent to
* You can also change the rate(30 minutes) to what ever you want... 
<br>you can find the rates syntax [here](https://docs.aws.amazon.com/AmazonCloudWatch/latest/events/ScheduledEvents.html)

#### And the magic happens once you execute this in your terminal:
```terminal
serverless deploy
```
It will pack all your files into .zip archive and upload to AWS, then it will create AWS CloudEvent to schedule and run the monitor automatically<br>

The serverless backend of your monitor is now live and running.<br>
Now if any asset or link in your website will be broken (Not found/ Server error / etc) you will get an email that's looks like that:

![Image of error email](https://i.ibb.co/ykHCxqC/Screenshot-2.png)

##### Also if there's any error accessing your target you will get an email like that:
![Image of error email](https://i.ibb.co/tx3342x/Screenshot-3.png)  

### Keep in mind

At the beginning it will cost you nothing, because The AWS Lambda free usage tier includes 400,000 GB-seconds of compute time per month.
<br>But if you have any other lambda function or multiply the monitors it can get to a point where they charge you...
<br>Our current usage is 60/30 * 60 * 24 * 30 = 86,400 calls 
each calls is between 1-5 seconds depends on the assets amount and a usage of 256MB
<br>So 86,400 * 3 (Average)  / 4 (GB-sec / 256MB = 3.9xxx) = 66,355 seconds of usage per month

## Credits
* [Serverless Framework](https://serverless.com/)
* Amazon AWS Lambda, CloudWatch and SES
