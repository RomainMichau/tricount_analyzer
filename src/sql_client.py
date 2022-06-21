from datetime import datetime

import psycopg2
from dataclasses import dataclass

from src.tricount_entity import Tricount

GET_TRICOUNT_BY_UUID = """
    SELECT id, tr_uuid, title
FROM public.tricount WHERE tr_uuid = %s ;
"""

GET_EXPENSES_PER_TRICOUNT = """
SELECT id, tr_id, addeddate, tr_exp_id, amount, "name"
FROM public.expenses WHERE tr_id = %s ;
"""

GET_IMPACT_PER_TRICOUNTS = """
SELECT i.id as impact_id, exp_id, "User", i.amount as impact_amount
FROM public.impacts as i join public.expenses as e on i.exp_id = e.id  WHERE e.tr_id = %s;
"""

INSERT_TRICOUNT = """
    INSERT INTO public.tricount
(tr_uuid, title)
VALUES(%s, %s) RETURNING id;
"""

UPDATE_TRICOUNT_TITLE = """
UPDATE public.tricount
SET title= %s
WHERE id=%s;
"""


@dataclass
class TricountSql:
    id: int
    uuid: str
    title: str


@dataclass
class ExpenseSql:
    id: int
    tr_id: int
    added_date: datetime
    tr_exp_id: int
    amount: int
    name: str


class SqlClient:
    def __init__(self):
        self.conn = psycopg2.connect(
            host="192.168.1.68",
            database="tricount",
            user="postgres",
            password="<BLK>")

    def get_tricount_by_uuid(self, uuid):
        cur = self.conn.cursor()
        cur.execute(GET_TRICOUNT_BY_UUID, (uuid,))
        sql_res = cur.fetchone()
        if sql_res is None:
            return None
        res = TricountSql(sql_res[0], sql_res[1], sql_res[2])
        cur.close()
        return res

    def get_expenses_for_tr(self, tricount_id):
        cur = self.conn.cursor()
        cur.execute(GET_EXPENSES_PER_TRICOUNT, (tricount_id,))
        sql_res = cur.fetchall()
        if sql_res is None:
            return None
        res = []
        for r in sql_res:
            res.append(ExpenseSql(sql_res[0], sql_res[1], sql_res[2], sql_res[3], sql_res[4], sql_res[5]))
        cur.close()
        return res

    def create_tricount(self, title, uuid):
        cur = self.conn.cursor()
        cur.execute(INSERT_TRICOUNT, (uuid, title))
        id_of_new_row = cur.fetchone()[0]
        self.conn.commit()
        cur.close()
        return TricountSql(id_of_new_row, uuid, title)

    def update_tricount_title(self, tricount_id, new_title):
        cur = self.conn.cursor()
        cur.execute(UPDATE_TRICOUNT_TITLE, (new_title, tricount_id))
        self.conn.commit()
        cur.close()

    def sync_tricount(self, tricount_target: Tricount):
        tricount_sql = self.get_tricount_by_uuid(tricount_target.uuid)
        if tricount_sql is None:
            tricount_sql = self.create_tricount(tricount_target.title, tricount_target.uuid)
        if tricount_sql.title != tricount_target.title:
            self.update_tricount_title(tricount_sql.id, tricount_target.title)



SqlClient().create_tricount("test_insert", "124c226c-2352-4d1f-9b43-bf7cfca5efcd", )
