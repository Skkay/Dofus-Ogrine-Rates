from bs4 import BeautifulSoup
from collections import OrderedDict
from datetime import datetime
from json import JSONDecoder
import requests
import yaml

def getLatestOgrineValues():
    url = "https://www.dofus.com/fr/achat-kamas/cours-kama-ogrines"
    headers = { 'User-Agent': 'Mozilla/5.0' }
    content = requests.get(url, headers=headers).text
    soup = BeautifulSoup(content)

    for script in soup.head.find_all('script'):
        if str(script).startswith('<script type="text/javascript">\n    RATES = '):
            str_rates = str(script)
            begin = str_rates.find("{")
            end = str_rates.find("}")
            rates = JSONDecoder(object_pairs_hook=OrderedDict).decode(str_rates[begin:end+1])

            return {'timestamp': list(rates)[-2], 'currentRate': rates[list(rates)[-2]], 'previousRate': rates[list(rates)[-3]]}


def writeToCsv(csv, timestamp, rate):
    with open(csv, 'a') as f:
        f.write(str(timestamp) + ',' + str(rate) + '\n')


def sendToDiscord(url, message):
    try:
        response = requests.post(url, data={'content': message})
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(e)


with open("config.yaml") as f:
    config = yaml.safe_load(f)

data = getLatestOgrineValues()
timestamp = data['timestamp']
localeDate = datetime.fromtimestamp(int(timestamp)/1000).strftime('%d %B %Y')
currentRate = data['currentRate']
rateChange = data['currentRate'] - data['previousRate']
rateChangePercent = rateChange / data['previousRate'] * 100

writeToCsv(config['csv_path'], timestamp, currentRate)

if rateChangePercent >= 0:
    message = f"**{localeDate}** : 1 Ogrine = **{currentRate}** Kama{'s' if currentRate >= 2 else ''}. *(+{rateChange} Kama{'s' if rateChange >= 2 else ''}, +{round(rateChangePercent, 2)}%)*"
else:
    message = f"**{localeDate}** : 1 Ogrine = **{currentRate}** Kama{'s' if currentRate >= 2 else ''}. *({rateChange} Kama{'s' if abs(rateChange) >= 2 else ''}, {round(rateChangePercent, 2)}%)*"

for webhook in config['webhooks']:
    sendToDiscord(webhook, message)
