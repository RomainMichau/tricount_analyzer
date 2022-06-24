import requests
from tricount_entity import Tricount
import logging


class ApiClient:
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'apisubversion': '102220'
    }

    def get_tricount_model(self, tricount_id) -> Tricount:
        try:
            data = f"getTricount=<tricount><id>0</id><random>{tricount_id}</random><description></description><users/><expenses/><versionNumber>0</versionNumber></tricount>"

            response = requests.post('https://api.tricount.com/api/v1/synchronisation/tricount/', headers=self.headers,
                                     data=data)
            response.raise_for_status()
            return Tricount(response.text)
        except Exception as e:
            logging.error(f"Got error message from Tricount API when trying to fetch tricount {tricount_id}.", e)
            raise e
