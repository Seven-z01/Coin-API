import requests

from .settings import URL, APIKEY


class APIError(Exception):
    pass


class CriptoValueModel():
    def __init__(self):
        self.input = ''
        self.output = ''
        self.value = 0.0
        self.json_dict = {}

    def get_value(self):
        header = {"X-CoinAPI-Key": APIKEY}
        answer = requests.get(URL.format(self.input, self.output), headers=header)

        if answer.status_code == 200:
            self.value = answer.json()['rate']
            self.json_dict = answer.text

        else:
            print(answer.json())
            raise APIError(f"There was an error {answer.status_code} in the request.")
