import logging

import requests
import xml.etree.ElementTree as ET
import argparse
from controller import Controller
from src.apli_client import ApiClient
from src.scheduler import Scheduler
from src.sql_client import SqlClient
from tricount_entity import Tricount

logging.getLogger().setLevel(logging.INFO)


def get_tricount_model(tricount_id):
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'apisubversion': '102220'
    }

    data = f"getTricount=<tricount><id>0</id><random>{tricount_id}</random><description></description><users/><expenses/><versionNumber>0</versionNumber></tricount>"

    response = requests.post('https://api.tricount.com/api/v1/synchronisation/tricount/', headers=headers, data=data)
    root = ET.fromstring(response.text)
    print(root.find("users").findall("user"))
    tr = Tricount(response.text)
    return tr


def main():
    parser = argparse.ArgumentParser(description='parse arg')
    parser.add_argument('--self_port', dest='self_port', type=str,
                        help='port used to run the app', default=8080)
    parser.add_argument('--db_hostname', dest='db_hostname', type=str,
                        help='db hostname', required=True)
    parser.add_argument('--db_password', dest='db_password', type=str,
                        help='db password', required=True)
    parser.add_argument('--db_user', dest='db_user', type=str,
                        help='db user. Need rw access', required=True)
    parser.add_argument('--db_port', dest='db_port', type=int,
                        help='db port', default="5432")
    parser.add_argument('--db_name', dest='db_name', type=str,
                        help='db name', default="tricount")
    parser.add_argument('--refresh_rate', dest='refresh_rate', type=int,
                        help='Interval of data refresh_rate', default=10)
    parser.add_argument('--admin_password', dest='admin_password', type=str,
                        help='Password of the user allowed to perform admin action on endpoints', required=True)
    parser.add_argument('--user_password', dest='user_password', type=str,
                        help='Password of the user allowed to perform standard action on endpoints', required=True)
    parser.add_argument('--tricount_max_nb', dest='tricount_max_nb', type=int,
                        help='max number of tricount allowed in the db', default=10)
    args = parser.parse_args()
    api_client = ApiClient()
    sql_client = SqlClient(args.db_hostname, args.db_user, args.db_password, args.db_name, args.db_port)
    Scheduler(sql_client, api_client, args.refresh_rate)
    Controller(args.self_port, api_client, sql_client, args.tricount_max_nb, args.user_password, args.admin_password, args.refresh_rate)


if __name__ == "__main__":
    main()
