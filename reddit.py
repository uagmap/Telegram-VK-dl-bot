#this file is responsible for getting daily top posts titles from r/AskReddit and translating it to Russian

import os
import requests
from googletrans import Translator



p_script = os.environ['personal_script']
secret = os.environ['secret']
username = os.environ['my_reddit_username']
password = os.environ['my_reddit_password']

translator = Translator()


#this block below is for redit authorization

# note that CLIENT_ID refers to 'personal use script' and SECRET_TOKEN to 'token'
auth = requests.auth.HTTPBasicAuth(p_script, secret)

# here we pass our login method (password), username, and password
data = {'grant_type': 'password',
        'username': username,
        'password': password}

# setup our header info, which gives reddit a brief description of our app
headers = {'User-Agent': 'MyBot/0.0.1'}

# send our request for an OAuth token
res = requests.post('https://www.reddit.com/api/v1/access_token',
                    auth=auth, data=data, headers=headers)

# convert response to JSON and pull access_token value
TOKEN = res.json()['access_token']

# add authorization to our headers dictionary
headers = {**headers, **{'Authorization': f"bearer {TOKEN}"}}

# while the token is valid (~2 hours) we just add headers=headers to our requests
requests.get('https://oauth.reddit.com/api/v1/me', headers=headers)






#this is the request of the top post of the day
def get_qotd():
  res = requests.get("https://oauth.reddit.com/r/AskReddit/top/",
                     headers=headers, params = {'limit': '1'})
  
  for post in res.json()['data']['children']:
    qotd = post['data']['title']
  
  return qotd

def qotd_trans():
  qotd = get_qotd()
  qotd_trans = translator.translate(qotd, src='en', dest='ru')
  return qotd_trans.text
  






  
#this is supposed to return list of indexed posts, through which you can rotate (future development plan, not in use)
def change_qotd():
  res = requests.get("https://oauth.reddit.com/r/AskReddit/top/",
                     headers=headers)
  
  for post in res.json()['data']['children']:
    print(post['data']['title'])
  