import requests
import xml.etree.ElementTree as ET

from controller import Controller
from tricount_anaylzer import TricountAnalyzer
from tricount_entity import Tricount


def get_tricount_model(tricount_id):
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
    }

    data = f"getTricount=<tricount><id>0</id><random>{tricount_id}</random><description></description><users/><expenses/><versionNumber>0</versionNumber></tricount>"

    response = requests.post('https://api.tricount.com/api/v1/synchronisation/tricount/', headers=headers, data=data)
    root = ET.fromstring(response.text)
    print(root.find("users").findall("user"))
    tr = Tricount(response.text)
    return tr




def main():
    tricount = get_tricount_model("BLk")
    Controller(8080, TricountAnalyzer(tricount))



if __name__ == "__main__":
    main()
