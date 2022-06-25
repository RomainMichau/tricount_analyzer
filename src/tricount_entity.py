import xml.etree.ElementTree as xml
from datetime import date, datetime

from dateutil import parser


class Impact:
    amount_tr_currency: float
    user: str

    def __init__(self, user: str, amount_tr_currency: float) -> None:
        self.user = user
        self.amount_tr_currency = amount_tr_currency


class Expense:
    added_date: datetime
    amount_tr_currency: float
    amount_exp_currency: float
    exp_currency: float
    exchange_rate: float
    name: str
    uuid: str
    paied_by: str
    paied_date: datetime
    impacts: list[Impact]

    def __init__(self, added_date: str, amount_exp_currency: float, name: str, paied_by: str, paied_date: str,
                 transaction_type: str,
                 impacts: list[Impact], uuid: str, amount_tr_currency: float, exchange_rate: float, exp_currency: str) -> None:
        self.added_date = parser.parse(added_date)
        self.amount_exp_currency = amount_exp_currency
        self.exp_currency = exp_currency
        self.amount_tr_currency = amount_tr_currency
        self.name = name
        self.uuid = uuid
        self.paied_by = paied_by
        self.paied_date = parser.parse(paied_date)
        self.impacts = impacts
        self.exchange_rate = exchange_rate
        self.transaction_type = transaction_type


class Tricount:
    currency: str
    title: str
    description: str
    users: list[str]
    expenses: list[Expense]
    uuid: str

    def __init__(self, xml_str: str):
        root = xml.fromstring(xml_str)
        self.currency = root.find("currency").text
        self.title = root.find("title").text
        if root.find("description") is None:
            self.description = root.find("title").text
        else:
            self.description = root.find("description").text
        self.uuid = root.find("uuid").text
        self.tr_id = root.find("random").text
        self.users = [user.find("name").text for user in root.find("users").findall("user")]
        self.expenses = list()
        for expense in root.find("expenses").findall("expense"):
            impacts = list()
            expense_id = expense.find("id").text
            if expense.find("transactionType").text != "NORMAL":
                continue
            impacts_xml = expense.find("repartition").findall("impact")
            exp_currency = expense.find("currency").text
            exchange_rate = float(expense.find("exchangeRate").text)
            amount_exp_currency = float(expense.find("amount").text)
            amount_tr_currency = amount_exp_currency * exchange_rate
            total_parts = 0.0
            already_defined_amount = 0.0
            for impact in impacts_xml:

                if impact.find("amountOfParts") is not None:
                    total_parts += int(impact.find("amountOfParts").text)
                else:
                    already_defined_amount += float(impact.find("amount").text)
            for impact in impacts_xml:
                user = impact.find("user").text
                if impact.find("amount") is not None:
                    amount = float(impact.find("amount").text) * exchange_rate
                    impacts.append(Impact(user, amount))
                else:
                    amount_of_part_for_impact = float(impact.find("amountOfParts").text)
                    amount = ((
                                      amount_exp_currency - already_defined_amount) / total_parts * amount_of_part_for_impact) * exchange_rate
                    impacts.append(Impact(user, amount))
            try:
                # paied date may be empty on old transaction
                if expense.find("paiedDate") is None:
                    paied_date = expense.find("addedDate").text
                else:
                    paied_date = expense.find("addedDate").text
                new_exp = Expense(expense.find("addedDate").text, amount_exp_currency,
                                  expense.find("name").text,
                                  expense.find("paiedBy").text, paied_date,
                                  expense.find("transactionType").text, impacts, expense.find("uuid").text,
                                  amount_tr_currency, exchange_rate, exp_currency)
            except Exception as e:
                print(f"Issue with expense:{expense_id}")
                raise e
            self.expenses.append(new_exp)
