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


def total_spent_over_date_range(df, start_date, end_date):

    df["Transaction Date"] = pd.to_datetime(
        df["Transaction Date"], format="%m/%d/%Y"
    )  # change to datetime obj
    transaction_range = df[  # use only the rows within the date range
        (df["Transaction Date"] >= start_date) & (df["Transaction Date"] <= end_date)
    ]
    total = (
        transaction_range[transaction_range["Transaction Type"] == "W"]["Amount"]
        .apply(
            lambda x: Decimal(str(x))
        )  # apply decimal representation to avoid rounding errors
        .sum()
    )
    return total


def get_all_locations(df):
    unique_locations = df["Location"].unique()  # convert unique locations to np array
    for i, location in enumerate(unique_locations, start=1):  # shows unique locations
        print(f"{i}. {location}")


def total_spent_at_location(df, location):  # calculates total at location
    filtered_locations = df[  # use only the rows corresponding to the location given
        (df["Location"] == location)
    ]
    total = (
        filtered_locations[filtered_locations["Transaction Type"] == "W"]["Amount"]
        .apply(
            lambda x: Decimal(str(x))
        )  # apply decimal representation to avoid rounding errors
        .sum()
    )
    return total


def main():
    # Read the transaction.txt - dummy_transactions.txt for testing
    transactions_file = open("transactions/dummy_transactions.txt", "r")
    transaction_lines = transactions_file.readlines()

    dates, locations, trans_types, amounts, balances = extract_categories(
        transaction_lines
    )

    print("*************** dataframe *************** ")
    df = create_dataframe(dates, locations, trans_types, amounts, balances)
    print(create_dataframe(dates, locations, trans_types, amounts, balances))
    print("*************** total spent *************** ")
    print(
        total_spent(create_dataframe(dates, locations, trans_types, amounts, balances))
    )
    start_date = "10/15/23"
    end_date = "11/10/23"
    print(total_spent_over_date_range(df, start_date=start_date, end_date=end_date))
    print("the unique locations>>>>>")
    get_all_locations(df)
    print("*************total spent at location*******************")
    print(total_spent_at_location(df, "Coffee Shop"))


if __name__ == "__main__":
    main()
