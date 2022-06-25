import logging
import threading
import time
import schedule

from src.apli_client import ApiClient
from src.sql_client import SqlClient


class Scheduler:
    def __init__(self, sql: SqlClient, api_client: ApiClient, refresh_rate: int):
        self.__sync_interval_min = refresh_rate
        self.sql = sql
        self.api_client = api_client
        thread = threading.Thread(target=self.run, args=())
        thread.name = "trilyzer sync"
        thread.start()

    def run(self):
        self.__sync_job()
        while True:
            schedule.run_pending()
            time.sleep(10)

    def __sync_job(self):
        schedule.every(self.__sync_interval_min).minutes \
            .do(self.launch_sync)

    def launch_sync(self):
        logging.info("Launching sync")
        try:
            tricounts_sql = self.sql.get_existing_tricounts()
            for tricount_sql in tricounts_sql:
                logging.info(f"syncing tricount {tricount_sql.title} / {tricount_sql.uuid}")

                tricount = self.api_client.get_tricount_model(tricount_sql.tr_id)
                self.sql.sync_tricount(tricount)
        except Exception as e:
            logging.error("Sync failed", e)
