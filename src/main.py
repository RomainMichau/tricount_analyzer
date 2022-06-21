import requests
import xml.etree.ElementTree as ET
import argparse
from controller import Controller
from src.sql_client import SqlClient
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
    parser = argparse.ArgumentParser(description='parse arg')
    parser.add_argument('--tricount_id', dest='tricount_id', type=str,
                        help='sum the integers (default: find the max)', default="UchqKYtTqgURBikxe")
    parser.add_argument('--db_password', dest='db_password', type=str,
                        help='sum the integers (default: find the max)')
    args = parser.parse_args()
    tricount_id = args.tricount_id
    print(tricount_id)
    tricount = get_tricount_model(args.tricount_id)
    SqlClient(args.db_password).sync_tricount(tricount)
    Controller(8080, TricountAnalyzer(tricount))


if __name__ == "__main__":
    main()
