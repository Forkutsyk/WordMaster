import requests
from utils.config import API_KEY, DICTIONARY_TYPE


class DictionaryAPI:
    BASE_URL = "https://www.dictionaryapi.com/api/v3/references/{dict_type}/json/{word}"

    def __init__(self):
        self.api_key = API_KEY
        self.dict_type = DICTIONARY_TYPE

    def get_definition(self, word):
        url = self.BASE_URL.format(dict_type=self.dict_type, word=word)
        params = {'key': self.api_key}

        response = requests.get(url, params=params)

        if response.status_code == 200:
            data = response.json()
            if data and isinstance(data[0], dict):
                return data[0].get('shortdef', ['No definition found'])[0]
            else:
                return "No definition found"
        else:
            return f"Error: {response.status_code}"