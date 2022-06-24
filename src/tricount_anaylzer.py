from tricount_entity import Tricount
import time
import datetime


class TricountAnalyzer:
    def __init__(self, tricount: Tricount):
        self.metrics = ["expense_total", "expense_per_user"]
        self.tricount = tricount

    def get_metrics(self):
        return self.metrics

    def answer_query(self, target, scoped_var):
        res = []
        if target == "expense_per_user":
            users = scoped_var["users"]["value"]
            for user in users:
                metrics = self.get_all_expenses_per_date_per_user(user)

                res.append({
                    "target": user,
                    "datapoints": metrics
                })
        elif target == "expense_total":
            metrics = self.get_all_expenses_per_date()
            res.append({
                "target": "Total",
                "datapoints": metrics
            })
        return res

    def get_all_expenses_per_date(self):
        res = []
        for expense in self.tricount.expenses:
            date_unit = int(expense.paied_date.timestamp()) * 1000
            res.append([float(expense.amount), date_unit])
        return res

    def get_all_expenses_per_date_per_user(self, user: str):
        res = []
        for expense in self.tricount.expenses:
            for impact in expense.impacts:
                if impact.user == user:
                    date_unit = int(expense.paied_date.timestamp()) * 1000
                    res.append([float(impact.amount_tr_currency), date_unit])
        return res

    def get_users(self):
        return self.tricount.users
