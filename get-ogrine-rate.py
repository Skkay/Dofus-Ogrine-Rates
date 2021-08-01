from bs4 import BeautifulSoup
from collections import OrderedDict
from datetime import datetime
from json import JSONDecoder
import locale
import logging
import requests
import yaml

def main():
    with open("config.yaml") as f:
        config = yaml.safe_load(f)

    locale.setlocale(locale.LC_TIME, "fr_FR.utf8")
    logging.basicConfig(filename=config['log_path'], encoding='utf-8', level=logging.DEBUG, format='[%(asctime)s.%(msecs)03d] %(levelname)s:%(module)s:%(funcName)s => %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

    data = getLatestOgrineValues()
    timestamp = data['timestamp']
    localeDate = datetime.fromtimestamp(int(timestamp)/1000).strftime('%d %B %Y')
    currentRate = data['currentRate']
    rateChange = data['currentRate'] - data['previousRate']
    rateChangePercent = rateChange / data['previousRate'] * 100

    writeToCsv(config['csv_path'], timestamp, currentRate)

    if rateChangePercent >= 0:
        message = f"**{localeDate}** : 1 Ogrine = **{currentRate}** Kama{'s' if currentRate >= 2 else ''}. *(+{round(rateChange, 1)} Kama{'s' if rateChange >= 2 else ''}, +{round(rateChangePercent, 2)}%)*"
    else:
        message = f"**{localeDate}** : 1 Ogrine = **{currentRate}** Kama{'s' if currentRate >= 2 else ''}. *({round(rateChange, 1)} Kama{'s' if abs(rateChange) >= 2 else ''}, {round(rateChangePercent, 2)}%)*"

    for webhook in config['webhooks']:
        sendToDiscord(webhook, message)


def getLatestOgrineValues():
    url = "https://www.dofus.com/fr/achat-kamas/cours-kama-ogrines"
    headers = { 'User-Agent': 'Mozilla/5.0' }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()

        content = response.text
        soup = BeautifulSoup(content)
        for script in soup.head.find_all('script'):
            if str(script).startswith('<script type="text/javascript">\n    RATES = '):
                str_rates = str(script)
                begin = str_rates.find("{")
                end = str_rates.find("}")
                rates = JSONDecoder(object_pairs_hook=OrderedDict).decode(str_rates[begin:end+1])
                data = {'timestamp': list(rates)[-2], 'currentRate': rates[list(rates)[-2]], 'previousRate': rates[list(rates)[-3]]}

                if data['currentRate'] == None:
                    logging.error('No value was found for the current rate (null)')
                    raise Exception('No value was found for the current rate (null)')

                logging.info(f'Successfully fetch Ogrine values: {data=}')
                return data

        logging.error('No <script> tag containing "RATES" was found')
        raise Exception('No <script> tag containing "RATES" was found')
    except requests.exceptions.Timeout as e:
        logging.error(f'Timeout: {str(e)}')
        raise
    except requests.exceptions.HTTPError as e:
        logging.error(f'HTTPError: {str(e)}')
        raise
    except requests.exceptions.RequestException as e:
        logging.error(f'RequestException: {str(e)}')
        raise


def writeToCsv(csv, timestamp, rate):
    with open(csv, 'a') as f:
        f.write(str(timestamp) + ',' + str(rate) + '\n')
        logging.info(f'Successfully write to "{csv}": {timestamp=}, {rate=}')


def sendToDiscord(url, message):
    try:
        response = requests.post(url, data={'content': message})
        response.raise_for_status()
        logging.info(f'Successfully sent to Discord using webhook "{url}": {message=}')
    except requests.exceptions.Timeout as e:
        logging.error(f'Timeout: {str(e)}')
    except requests.exceptions.HTTPError as e:
        logging.error(f'HTTPError: {str(e)}')
    except requests.exceptions.RequestException as e:
        logging.error(f'RequestException: {str(e)}')


if __name__ == "__main__":
    main()
