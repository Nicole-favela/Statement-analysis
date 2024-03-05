import re
import pandas as pd
import os
from decimal import Decimal


def extract_categories(blocks):  # add each line to category and return lists
    # categories
    dates = []
    locations = []
    amounts = []
    balances = []
    types = []  # W for withdrawl, D for deposit

    for block in blocks:
        # line = block.split("\n")
        block = block.strip()

        # Extract date
        if re.match(r"\d{2}/\d{2}/\d{4}", block):
            dates.append(block)

        # Extract withdrawal location and type
        elif block.startswith("Withdrawal") or block.startswith("Deposit"):
            location_info = block.split(" ")
            locations.append(
                " ".join(location_info[1:-3])
            )  # Extracting location from the middle of the string
            if block.startswith("Withdrawal"):
                types.append("W")
            elif block.startswith("Deposit"):
                types.append("D")

        # Extract amount-what is deposited/withdrew
        elif block.startswith("-$") or block.startswith("+"):
            amount = float(block.replace("-$", "").replace("+$", ""))
            amounts.append(amount)

        # Extract balance and remove $ and ,
        elif block.startswith("$"):
            balance = float(block.replace("$", "").replace(",", ""))
            balances.append(balance)

    return dates, locations, types, amounts, balances


def create_dataframe(dates, locations, types, amounts, balances):
    df = pd.DataFrame(
        list(zip(dates, locations, types, amounts, balances)),
        columns=[
            "Transaction Date",
            "Location",
            "Transaction Type",
            "Amount",
            "Balance",
        ],
    )
    return df


def total_spent(df):  # calculates total withdrawls

    total = (
        df[df["Transaction Type"] == "W"]["Amount"]
        .apply(
            lambda x: Decimal(str(x))
        )  # apply decimal representation to avoid rounding errors
        .sum()
    )
    return total


# TODO: total over date range


def main():
    # Read the transaction.txt - dummy_transactions.txt for testing
    transactions_file = open("transactions/dummy_transactions.txt", "r")
    transaction_lines = transactions_file.readlines()

    dates, locations, trans_types, amounts, balances = extract_categories(
        transaction_lines
    )
    # for date, location, trans_type, amount, balance in zip(
    #     dates, locations, trans_types, amounts, balances
    # ):
    #     print("Date:", date)
    #     print("Location:", location)
    #     print("Types:", trans_type)
    #     print("Amount:", amount)
    #     print("Balance:", "{:.2f}".format(balance))
    #     print("------")
    print("*************** dataframe *************** ")
    print(create_dataframe(dates, locations, trans_types, amounts, balances))
    print("*************** total spent *************** ")
    print(
        total_spent(create_dataframe(dates, locations, trans_types, amounts, balances))
    )


if __name__ == "__main__":
    main()
