import pandas as pd
from datetime import datetime


def choose_option(options):
    for i, option in enumerate(options, start=1):
        print(f"{i}. {option}")
    while True:
        try:
            choice = int(input(f"Choose an option between 1 and {len(options)}: "))
            if 1 <= choice <= len(options):
                return options[choice - 1]
            else:
                print(
                    f"Please enter a number between 1 and {len(options)}."
                )  # Inform user of valid range
        except ValueError:
            print("Please enter a valid option.")


def check_date_input(df, prompt):
    while True:
        user_input = input(prompt)
        try:
            date_input = datetime.strptime(user_input, "%m/%d/%y")
            date = pd.to_datetime(date_input, format="%m/%d/%Y")

            df["Transaction Date"] = pd.to_datetime(
                df["Transaction Date"], format="%m/%d/%Y"
            )
            statement_start_date = df["Transaction Date"].min()
            statement_end_date = df["Transaction Date"].max()
            valid_range = date >= statement_start_date and date <= statement_end_date

            if valid_range:
                return date
            else:
                print(f"Error: that date is out of the range of your statement")
        except ValueError:
            print("Invalid date format. Please enter in the fomat MM/DD/YY")
