import xml.etree.ElementTree as xml
from datetime import date, datetime

from dateutil import parser


class Impact:
    amount: float
    user: str

    def __init__(self, user: str, amount: float) -> None:
        self.user = user
        self.amount = amount


class Expense:
    added_date: datetime
    amount: str
    name: str
    uuid: str
    paied_by: str
    paied_date: datetime
    repartition: list[Impact]

    def __init__(self, added_date: str, amount: str, name: str, paied_by: str, paied_date: str, transaction_type: str,
                 repartition: list[Impact], uuid: str) -> None:
        self.added_date = parser.parse(added_date)
        self.amount = amount
        self.name = name
        self.uuid = uuid
        self.paied_by = paied_by
        self.paied_date = parser.parse(paied_date)
        self.repartition = repartition
        self.transaction_type = transaction_type


class Tricount:
    currency: str
    title: str
    users: list[str]
    expenses: list[Expense]
    uuid: str

    def __init__(self, xml_str: str):
        root = xml.fromstring(xml_str)
        self.currency = root.find("currency").text
        self.title = root.find("title").text
        self.uuid = root.find("uuid").text
        self.title = root.find("description").text
        self.users = [user.find("name").text for user in root.find("users").findall("user")]
        self.expenses = list()
        for expense in root.find("expenses").findall("expense"):
            impacts = list()
            expense_id = expense.find("id").text
            impacts_xml = expense.find("repartition").findall("impact")
            total_amount = float(expense.find("amount").text)
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
                    amount = float(impact.find("amount").text)
                    impacts.append(Impact(user, amount))
                else:
                    amount_of_part_for_impact = float(impact.find("amountOfParts").text)
                    amount = (total_amount - already_defined_amount) / total_parts * amount_of_part_for_impact
                    impacts.append(Impact(user, amount))
            try:
                # paied date may be empty on old transaction
                if expense.find("paiedDate") is None:
                    paied_date = expense.find("addedDate").text
                else:
                    paied_date = expense.find("addedDate").text
                new_exp = Expense(expense.find("addedDate").text, expense.find("amount").text,
                                  expense.find("name").text,
                                  expense.find("paiedBy").text, paied_date,
                                  expense.find("transactionType").text, impacts, expense.find("uuid").text)
            except Exception as e:
                print(f"Issue with expense:{expense_id}")
                raise e
            self.expenses.append(new_exp)
