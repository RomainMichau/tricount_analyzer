from datetime import datetime

import psycopg2
from dataclasses import dataclass

from src.tricount_entity import Tricount

GET_TRICOUNT_BY_UUID = """
    SELECT tr_uuid, tr_id, title, tr_currency
FROM public.tricount WHERE tr_uuid = %s ;
"""

GET_ALL_TRICOUNT_BY_UUID = """
    SELECT tr_uuid, tr_id, title, tr_currency
FROM public.tricount;
"""

GET_EXPENSES_PER_TRICOUNT = """
SELECT  exp_uuid, tr_uuid, amount_tr_currency, amount_exp_currency, exchange_rate, exp_currency, "name", payed_by, addeddate
FROM public.expenses WHERE tr_uuid = %s ;
"""

GET_EXPENSES_PER_UUID = """
SELECT addeddate, amount, "name", exp_uuid, tr_uuid
FROM public.expenses WHERE tr_exp_uuid = %s ;
"""

GET_IMPACT_PER_EXP = """
SELECT e.tr_uuid, i.exp_uuid, i."User", i.amount_tr_currency
FROM public.impacts as i join public.expenses as e on i.exp_uuid = e.exp_uuid  WHERE e.exp_uuid = %s;
"""

INSERT_TRICOUNT = """
    INSERT INTO public.tricount
(tr_uuid, tr_id, title, description, tr_currency)
VALUES(%s, %s, %s, %s, %s) RETURNING id;
"""

INSERT_EXPENSE = """
INSERT INTO public.expenses
(exp_uuid, tr_uuid, amount_tr_currency, amount_exp_currency, exchange_rate, exp_currency, "name", payed_by, addeddate )
VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING id;
"""

INSERT_IMPACT = """
INSERT INTO public.impacts
(exp_uuid, "User", amount_tr_currency)
VALUES(%s, %s , %s) returning id;

"""

UPDATE_TRICOUNT_TITLE = """
UPDATE public.tricount
SET title= %s
WHERE tr_uuid=%s;
"""

DELETE_IMPACT_PER_EXP_UUID = """
DELETE FROM public.impacts WHERE exp_uuid = %s 
"""

DELETE_EXP_PER_TR_UUID = """
DELETE FROM public.expenses WHERE tr_uuid = %s
"""

DELETE_TRICOUNT_PER_TR_UUID = """
DELETE FROM public.tricount WHERE tr_uuid = %s
"""


@dataclass
class TricountSql:
    uuid: str
    tr_id: str
    title: str
    currency: str


@dataclass
class ExpenseSql:
    tr_uuid: int
    added_date: datetime
    amount_exp_currency: float
    amount_tr_currency: float
    name: str
    expense_uuid: str
    exp_currency: str
    exchange_rate: float


@dataclass
class ImpactSql:
    exp_uuid: str
    User: str
    amound: int


class SqlClient:
    def __init__(self, hostname, username, password, db_name, port=5432):
        self.conn = psycopg2.connect(
            host=hostname,
            database=db_name,
            user=username,
            password=password,
            port=port)

    def __get_tricount_by_uuid(self, uuid):
        cur = self.conn.cursor()
        cur.execute(GET_TRICOUNT_BY_UUID, (uuid,))
        sql_res = cur.fetchone()
        if sql_res is None:
            return None
        res = TricountSql(sql_res[0], sql_res[1], sql_res[2], sql_res[3])
        cur.close()
        return res

    # return dict : { exp_uuid -> exp }
    def __get_expenses_for_tr(self, tricount_uuid):
        cur = self.conn.cursor()
        cur.execute(GET_EXPENSES_PER_TRICOUNT, (tricount_uuid,))
        sql_res = cur.fetchall()
        if sql_res is None:
            return dict()
        res = dict()
        for r in sql_res:
            exp = ExpenseSql(r[1], r[8], r[3], r[2], r[6], r[0], r[5], r[4])
            res[exp.expense_uuid] = exp
        cur.close()
        return res

    # return dict : { User -> imp }
    def __get_impact_for_exp(self, exp_uuid):
        cur = self.conn.cursor()
        cur.execute(GET_IMPACT_PER_EXP, (exp_uuid,))
        sql_res = cur.fetchall()
        if sql_res is None:
            return dict()
        res = dict()
        for r in sql_res:
            imp = ImpactSql(r[1], r[2], r[3])
            res[imp.User] = imp
        cur.close()
        return res

    def __create_tricount(self, title, tr_id, uuid, description, tr_currrency):
        cur = self.conn.cursor()
        cur.execute(INSERT_TRICOUNT, (uuid, tr_id, title, description, tr_currrency))
        self.conn.commit()
        cur.close()

    def __create_expense(self, exp_uuid, tr_uuid, amount_tr_currency, amount_exp_currency, exchange_rate, exp_currency,
                         name, payed_by, addeddate):
        cur = self.conn.cursor()
        cur.execute(INSERT_EXPENSE, (
            exp_uuid, tr_uuid, amount_tr_currency, amount_exp_currency, exchange_rate, exp_currency, name, payed_by,
            addeddate))
        self.conn.commit()
        cur.close()

    def __create_impact(self, exp_uuid, user, amount_tr_currency):
        cur = self.conn.cursor()
        cur.execute(INSERT_IMPACT, (exp_uuid, user, amount_tr_currency))
        self.conn.commit()
        cur.close()

    def __update_tricount_title(self, tricount_id, new_title):
        cur = self.conn.cursor()
        cur.execute(UPDATE_TRICOUNT_TITLE, (new_title, tricount_id))
        self.conn.commit()
        cur.close()

    def delete_tricount(self, tr_uuid):
        cur = self.conn.cursor()
        for exp_uuid in self.__get_expenses_for_tr(tr_uuid):
            cur.execute(DELETE_IMPACT_PER_EXP_UUID, (exp_uuid,))
        cur.execute(DELETE_EXP_PER_TR_UUID, (tr_uuid,))
        cur.execute(DELETE_TRICOUNT_PER_TR_UUID, (tr_uuid,))
        self.conn.commit()
        cur.close()

    def sync_tricount(self, tricount_target: Tricount):
        tricount_sql = self.__get_tricount_by_uuid(tricount_target.uuid)
        if tricount_sql is None:
            self.__create_tricount(tricount_target.title, tricount_target.tr_id, tricount_target.uuid,
                                   tricount_target.description,
                                   tricount_target.currency)
        elif tricount_sql.title != tricount_target.title:
            self.__update_tricount_title(tricount_sql.uuid, tricount_target.title)
        sql_expenses = self.__get_expenses_for_tr(tricount_target.uuid)
        for expense in tricount_target.expenses:
            if expense.uuid not in sql_expenses:
                self.__create_expense(expense.uuid, tricount_target.uuid, expense.amount_tr_currency,
                                      expense.amount_exp_currency, expense.exchange_rate, expense.exp_currency,
                                      expense.name, expense.paied_by, expense.added_date)
            sql_impacts = self.__get_impact_for_exp(expense.uuid)
            for impact in expense.impacts:
                if impact.user not in sql_impacts:
                    self.__create_impact(expense.uuid, impact.user, impact.amount_tr_currency)

    def get_existing_tricount_uuids(self):
        cur = self.conn.cursor()
        cur.execute(GET_ALL_TRICOUNT_BY_UUID)
        sql_res = cur.fetchall()
        if sql_res is None:
            return list()
        res = list()
        for r in sql_res:
            res.append(r[0])
        cur.close()
        return res

    def get_existing_tricounts(self):
        cur = self.conn.cursor()
        cur.execute(GET_ALL_TRICOUNT_BY_UUID)
        sql_res = cur.fetchall()
        if sql_res is None:
            return list()
        res = list()
        for r in sql_res:
            res.append(TricountSql(r[0], r[1], r[2], r[3]))
        cur.close()
        return res
