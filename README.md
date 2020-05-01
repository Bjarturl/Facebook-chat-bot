# Facebook-chat-bot
Chat bot on a Facebook page. Sends menus to user and responds based on selection. Hosted on Heroku as a Flask app.
A big part of this project was learning the Facebook Graph API and getting an app submitted and approved by Facebook.
## Functionality
The functionalities include:
* An entertainment menu:
  * Meme: Fetches a funny meme from an API that gets its data from Reddit.
  * Roast: Fetches a "roast" from a roast API and adds the user's name to it. A roast is a joke revolved around critizising someone, often in a ridicilous/funny way.
  * Compliment: If the roast is bad you can get relief from the compliment menu. It also connects to an API and compliments you in some way.
* Offers right now menu:
  * Happy hours: Tells you where there is happy hour right now. This data is scraped from www.happyhour.is
  * Nova 2 for 1 offers: Tells you what Nova 2 for 1 offers are going on right now. This data is scraped from www.nova.is/dansgolfid/2fyrir1.
  * Cheapest gas: Tells you the top 10 cheapest gas stations and their prices. This data is fetched through an api from www.apis.is
