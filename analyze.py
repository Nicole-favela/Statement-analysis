import re
import pandas as pd
import os


def extract_categories(blocks):  # add each line to category and return lists
    # categories
    dates = []
    locations = []
    amounts = []
    balances = []

    for block in blocks:
        # line = block.split("\n")
        block = block.strip()
        print("this block is>>>>>>>>>>>>>>", block)

        # Extract date
        if re.match(r"\d{2}/\d{2}/\d{4}", block):
            dates.append(block)

        # Extract withdrawal location
        elif block.startswith("Withdrawal") or block.startswith("Deposit"):
            location_info = block.split(" ")
            locations.append(
                " ".join(location_info[1:-3])
            )  # Extracting location from the middle of the string

        # Extract amount-what is deposited/withdrew
        elif block.startswith("-$") or block.startswith("+"):
            amount = float(block.replace("-$", "").replace("+$", ""))
            amounts.append(amount)

        # Extract balance and remove $ and ,
        elif block.startswith("$"):
            balance = float(block.replace("$", "").replace(",", ""))
            balances.append(balance)

    return dates, locations, amounts, balances


def main():
    # Read the transaction.txt - dummy_transactions.txt for testing
    transactions_file = open("transactions/dummy_transactions.txt", "r")
    transaction_lines = transactions_file.readlines()

    dates, locations, amounts, balances = extract_categories(transaction_lines)
    for date, location, amount, balance in zip(dates, locations, amounts, balances):
        print("Date:", date)
        print("Location:", location)
        print("Amount:", amount)
        print("Balance:", balance)
        print("------")


if __name__ == "__main__":
    main()
