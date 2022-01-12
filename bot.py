import logging
import requests
import urllib3
import time
from datetime import datetime
from dotenv import dotenv_values

urllib3.disable_warnings()
config = dotenv_values(".env")


def check_stat():
    result = {
        'is_ok': False,
        'status': None,
        'message': None
    }
    url = "https://stat.gov.kz/api/juridical/counter/api/?bin={}&lang=ru".format(config.get('SAMPLE_BIN'))

    try:
        response = requests.get(url=url, verify=False, )
    except requests.ConnectionError as e:
        logging.error(e)
        result['message'] = e
        result['status'] = 500
        return result
    except requests.HTTPError as e:
        logging.error(e)
        result['message'] = e
        result['status'] = 500
        return result
    else:
        if response.status_code == requests.codes.ok:
            result['message'] = "Company with BIN {} found.".format(config.get('SAMPLE_BIN'))
            result['status'] = 200
            result['is_ok'] = True
            return result

        result['message'] = response.reason
        result['status'] = response.status_code
        return result


def check_pk_too():
    result = {
        'is_ok': False,
        'status': None,
        'message': None
    }
    url = "https://pk.uchet.kz:8001/api/company/get?client_id={}&bin={}".format(
        config.get('MSB_QA_PK_ID'),
        config.get('SAMPLE_BIN')
    )

    try:
        response = requests.get(url=url, verify=False, headers={
            'CLIENT_SECRET': config.get('MSB_QA_PK_SECRET')
        })
    except requests.ConnectionError as e:
        logging.error(e)
        result['message'] = e
        result['status'] = 500
        return result
    except requests.HTTPError as e:
        logging.error(e)
        result['message'] = e
        result['status'] = 500
        return result
    else:
        if response.status_code == requests.codes.ok:
            obj = response.json()
            if obj.get('error'):
                result['message'] = obj.get('error').get('message')
                result['status'] = 404
                return result

            elif obj.get('result'):
                result['message'] = "Company with BIN {} found.".format(config.get('SAMPLE_BIN'))
                result['status'] = 200
                result['is_ok'] = True
                return result

        result['message'] = response.reason
        result['status'] = response.status_code
        return result


def check_pk_ip():
    result = {
        'is_ok': False,
        'status': None,
        'message': None
    }
    url = "https://pk.uchet.kz:8001/api/person/get?client_id={}&iin={}".format(
        config.get('MSB_QA_PK_ID'),
        config.get('SAMPLE_IIN')
    )

    try:
        response = requests.get(url=url, verify=False, headers={
            'CLIENT_SECRET': config.get('MSB_QA_PK_SECRET')
        })
    except requests.ConnectionError as e:
        logging.error(e)
        result['message'] = e
        result['status'] = 500
        return result
    except requests.HTTPError as e:
        logging.error(e)
        result['message'] = e
        result['status'] = 500
        return result
    else:
        if response.status_code == requests.codes.ok:
            obj = response.json()
            if obj.get('error'):
                result['message'] = obj.get('error').get('message')
                result['status'] = 404
                return result

            elif obj.get('result'):
                result['message'] = "Company with IIN {} found.".format(config.get('SAMPLE_IIN'))
                result['status'] = 200
                result['is_ok'] = True
                return result

        result['message'] = response.reason
        result['status'] = response.status_code
        return result


def send_message_bot(text):
    url = "https://api.telegram.org/bot{}/sendMessage".format(config.get('MSB_QA_BOT_TOKEN'))
    parameters = {
        "chat_id": config.get('MSB_QA_CHAT_ID'),
        "text": text
    }

    try:
        response = requests.get(url=url, verify=False, params=parameters)
    except requests.ConnectionError as e:
        logging.error(e)
        return False
    except requests.HTTPError as e:
        logging.error(e)
        return False
    else:
        if response.status_code == requests.codes.ok:
            logging.info(msg=response.text)
            return True
        return False


if __name__ == '__main__':
    tag = '#stable'
    greet_txt = "\U0001F197 Everything is stable \U0001F197"
    while True:
        logging.info('Checking Stat Gov')
        stat_data = check_stat()
        logging.info('Checking PK TOO')
        pk_too_data = check_pk_too()
        logging.info('Checking PK IP')
        pk_ip_data = check_pk_ip()
        if (stat_data.get('is_ok') and pk_too_data.get('is_ok') and pk_ip_data.get('is_ok')) is False:
            tag = '#error'
            greet_txt = "\U0001F198 Found error, @rruss \U0001F198"
        text = f"{greet_txt}\n" \
               f"[{datetime.now()}]\n" \
               "stat.gov.kz: \n" \
               f"{stat_data}\n" \
               "\n" \
               f"pk.uchet.kz (For TOO):\n" \
               f"{pk_too_data}\n" \
               "\n" \
               f"pk.uchet.kz (For IP):\n" \
               f"{pk_ip_data}\n" \
               f"{tag}\n" \
               f"---------------------------------------------------------"
        send_message_bot(text)
        time.sleep(int(config.get('INTERVAL_SEC')))
