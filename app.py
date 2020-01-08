import random, requests, json
from flask import Flask, request
from pymessenger.bot import Bot
from pymessenger import Button
import urllib.request
from datetime import datetime
from bs4 import BeautifulSoup as bs


app = Flask(__name__)
ACCESS_TOKEN = 'REDACTED'
VERIFY_TOKEN = 'REDACTED'
bot = Bot(ACCESS_TOKEN)


@app.route('/', methods=['GET', 'POST'])
#Handle requests sent to endpoint
def receiveMessage():
    if request.method == 'GET':
        token_sent = request.args.get("hub.verify_token")
        return verifyFbToken(token_sent)
    else: #POST
        output = request.get_json() #request content
        if 'postback' in output['entry'][0]['messaging'][0]: #user clicked a button  
            received = output['entry'][0]['messaging'][0]['postback']['payload']
            user_id = output['entry'][0]['messaging'][0]['sender']['id']
            user_details = getUserDetails(user_id)
            response, link = getResponse(received, user_details, user_id) #get message to reply with
            sendMessage(user_id, response, link)
        else:
            for event in output['entry']: 
                messaging = event['messaging']
                for message in messaging:
                    if message.get('message'): #If user sent us a message
                        user_id = message['sender']['id']
                        user_details = getUserDetails(user_id)
                        if message['message'].get('text'): #If user sent us a text message
                            received = message['message'].get('text')
                            response, link = getResponse(received, user_details, user_id)
                            sendMessage(user_id, response, link)
                        if message['message'].get('attachments'): #If user sent us a photo or gif
                            received = ""
                            response, link = getResponse(received, user_details, user_id)
                            sendMessage(user_id, response, link)
    return ""


#Ensures request has the correct token
def verifyFbToken(token_sent):
    if token_sent == VERIFY_TOKEN:
        return request.args.get("hub.challenge")
    return ""


#Get basic information about user who sent the message
def getUserDetails(user_id):
    user_details_url = "https://graph.facebook.com/v2.6/%s"%user_id
    user_details_params = {'fields':'first_name,middle_name,last_name,profile_pic', 'access_token':ACCESS_TOKEN}
    return requests.get(user_details_url, user_details_params).json()


#Sends entertainment menu to user
def sendEntertainmentMenu(user_id):
    buttons = []
    button = Button(title='Meme', type='postback', payload='Meme')
    buttons.append(button)
    button = Button(title='Roast', type='postback', payload='Roast')
    buttons.append(button)
    button = Button(title='Compliment', type='postback', payload='Compliment')
    buttons.append(button)
    text = 'Welcome to the entertainment menu!\n'
    text += 'Please select an option:'
    bot.send_button_message(user_id, text, buttons)


#Sends offer menu to user
def sendOfferMenu(user_id):
    buttons = []
    button = Button(title='Happy hours', type='postback', payload='Happy hours')
    buttons.append(button) 
    button = Button(title='Nova 2 for 1 offers', type='postback', payload='Nova 2 for 1 offers')
    buttons.append(button) 
    text = 'Below are offers happening RIGHT NOW!\n'
    text += 'Please select an option:'
    bot.send_button_message(user_id, text, buttons)


#Send menu options to user
def sendMainMenu(user_id):
    buttons = []
    button = Button(title='Entertainment', type='postback', payload='Entertainment')
    buttons.append(button) 
    button = Button(title='Offers right now', type='postback', payload='$$$')
    buttons.append(button) 
    text = 'Below are the available menus.\n'
    text += 'Please select an option:'
    bot.send_button_message(user_id, text, buttons)


#Determine how to respond to user
def getResponse(received, user_details, user_id):
    image = False #determine whether response is an image or not
    if received.lower() == "entertainment":
        response = ""
        sendEntertainmentMenu(user_id)
    elif received.lower() == "$$$":
        response = ""
        sendOfferMenu(user_id)
    elif received.lower() == "meme":
        response = getMeme()
        image = True
    elif received.lower() == "roast":
        response = getRoast(user_details['first_name'])
    elif received.lower() == "compliment":
        response = getCompliment(user_details['first_name'])
    elif received.lower() == "nova 2 for 1 offers":
        response = getNovaOffers()
    elif received.lower() == "happy hours":
        response = getHappyHour()
    else:
        response = ""
        sendMainMenu(user_id)
    return response, image 


#Fetch meme from randomly chosen API
def getMeme():
    meme_sites = ["https://meme-api.glitch.me/moderate", "https://meme-api.glitch.me/light", "https://meme-api.glitch.me/dank"]
    link = random.choice(meme_sites)
    data = requests.get(link).content
    return json.loads(data.decode())['meme']


#Fetch random roast from API
def getRoast(name):
    link = "https://evilinsult.com/generate_insult.php?lang=en&type=json"
    data = requests.get(link).content
    insult = json.loads(data.decode())['insult']
    first = insult[0].lower() #first letter should not be capitalized
    insult = first + insult[1:] #remove weird char at start of string
    response = name + ", " + insult
    response = response.replace("&quot;","\"")
    return response.replace("--&gt;",">")


#Fetch random compliment from API
def getCompliment(name):
    link = "https://complimentr.com/api"
    data = requests.get(link).content
    meme = json.loads(data.decode())['compliment']
    return name + ", " + meme + "."


#Send image or message to user based on his choices
def sendMessage(user_id, response, link):
    if link:
        bot.send_image_url(user_id, response)
    else:
        bot.send_text_message(user_id, response)


#Scrape from Nova site which offers are happening now (filters applied at url)
def getNovaOffers():
    url = "https://www.nova.is/dansgolfid/2fyrir1?type=allt&time=nuna&location=h%C3%B6fu%C3%B0borgarsv%C3%A6%C3%B0inu"
    page = urllib.request.urlopen(url)
    parse = bs(page, 'lxml')
    response = ""
    for cont in parse.findAll("div", {"class": "_1e4fOW6b78"}):
        for a in cont.findAll("a", href=True):
            for h2 in a.findAll("h2"):
                response += h2.text + " (www.nova.is" + a['href'] + ")\n\n"
    return response[:-2]


#Scrape happy hour site to find current places that have happy hour going on
def getHappyHour():
    url = "https://www.happyhour.is/?time=today"
    page = urllib.request.urlopen(url)
    parse = bs(page, 'lxml')
    now = datetime.now().time()
    places = ""
    for a in parse.findAll("div", {"class": "coupon_frame"}):
        for i in a.findAll("div", {"class": "timedate"}):
            start = datetime.strptime(i.text[1:6], '%H:%M').time() #start time for selected place
            end = datetime.strptime(i.text[9:14], '%H:%M').time() #end time for selected place
            if now >= start and now <= end:
                    places += a.findAll("h3")[0].text + " (" + str(start)[0:5] + "-" + str(end)[0:5] + ")" + "\n\n"
    if places:
        return "Happy hours happening right now in Reykjavík are at:\n" + places[:-2]
    else:
        return "No bar or restaurant in Reykjavík has happy hour going on right now :("
    

#Only needs to be called once to set the get started menu to messenger
def set_get_started():
    request_endpoint = 'https://graph.facebook.com/v2.6/me/messenger_profile'
    gs_obj = { 
        "get_started":{
            "payload": "Get started"
        }
    }
    response = requests.post(
        request_endpoint,
        params = bot.auth_args,
        json = gs_obj
    )
    result = response.json()
    return result


#Only needs to be called once to set a persistent menu to messenger
def set_persistent_menu():
    pm_obj = {
        "persistent_menu": [
            {
                "locale": "default",
                "composer_input_disabled": False,
                "call_to_actions": [
                    {
                        "type": "postback",
                        "title": "Entertainment",
                        "payload": "Entertainment"
                    },
                    {
                        "type": "postback",
                        "title": "Offers right now",
                        "payload": "$$$"
                    }
                ]
            }
        ]
    }
    request_endpoint = 'https://graph.facebook.com/v2.6/me/messenger_profile'
    response = requests.post(
        request_endpoint,
        params = bot.auth_args,
        json = pm_obj
    )
    result = response.json()
    return result

if __name__ == "__main__":
    #set_get_started()
    #set_persistent_menu()
    app.run()