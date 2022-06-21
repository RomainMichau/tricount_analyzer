from datetime import datetime

import psycopg2
from dataclasses import dataclass

from src.tricount_entity import Tricount

GET_TRICOUNT_BY_UUID = """
    SELECT tr_uuid, title
FROM public.tricount WHERE tr_uuid = %s ;
"""

GET_EXPENSES_PER_TRICOUNT = """
SELECT  addeddate, amount, "name", exp_uuid, tr_uuid
FROM public.expenses WHERE tr_uuid = %s ;
"""

GET_EXPENSES_PER_UUID = """
SELECT addeddate, amount, "name", exp_uuid, tr_uuid
FROM public.expenses WHERE tr_exp_uuid = %s ;
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

INSERT_EXPENSE = """
INSERT INTO public.expenses
(addeddate, amount, "name", exp_uuid, tr_uuid)
VALUES(%s, %s, %s, %s, %s) RETURNING id;
"""

UPDATE_TRICOUNT_TITLE = """
UPDATE public.tricount
SET title= %s
WHERE id=%s;
"""


@dataclass
class TricountSql:
    uuid: str
    title: str


@dataclass
class ExpenseSql:
    tr_uuid: int
    added_date: datetime
    amount: int
    name: str
    expense_uuid: str


class SqlClient:
    def __init__(self, password):
        self.conn = psycopg2.connect(
            host="192.168.1.68",
            database="tricount",
            user="postgres",
            password=password)

    def get_tricount_by_uuid(self, uuid):
        cur = self.conn.cursor()
        cur.execute(GET_TRICOUNT_BY_UUID, (uuid,))
        sql_res = cur.fetchone()
        if sql_res is None:
            return None
        res = TricountSql(sql_res[0], sql_res[1])
        cur.close()
        return res

    # return dict : { exp_uuid -> exp }
    def get_expenses_for_tr(self, tricount_id):
        cur = self.conn.cursor()
        cur.execute(GET_EXPENSES_PER_TRICOUNT, (tricount_id,))
        sql_res = cur.fetchall()
        if sql_res is None:
            return None
        res = dict()
        for r in sql_res:
            exp = ExpenseSql(sql_res[3], sql_res[0], sql_res[1], sql_res[2], sql_res[4])
            res[exp.expense_uuid] = exp
        cur.close()
        return res

    def create_tricount(self, title, uuid) -> TricountSql:
        cur = self.conn.cursor()
        cur.execute(INSERT_TRICOUNT, (uuid, title))
        id_of_new_row = cur.fetchone()[0]
        self.conn.commit()
        cur.close()
        return TricountSql(uuid, title)

    def create_expense(self, tricount_uuid, added_date, amount, name, exp_uuid):
        cur = self.conn.cursor()
        cur.execute(INSERT_EXPENSE, (added_date, added_date, amount, name, exp_uuid))
        self.conn.commit()
        cur.close()
        return ExpenseSql(tricount_uuid, added_date, amount, name, exp_uuid)

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
        sql_expenses = self.get_expenses_for_tr(tricount_sql.id)

        for expense in tricount_target.expenses:
            if expense.uuid not in sql_expenses:
                self.create_expense(tricount_sql.id, expense.added_date, expense.amount, expense.name, expense.uuid)
