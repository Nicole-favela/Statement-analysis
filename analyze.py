import re
import pandas as pd
import os
from decimal import Decimal
import matplotlib.pyplot as plt
import argparse


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


def choose_option(options):
    for i, option in enumerate(options, start=1):
        print(f"{i}. {option}")
    choice = int(input("Choose an option: "))
    return options[choice - 1]


def get_all_locations(df, flag):
    unique_locations = df["Location"].unique()  # convert unique locations to np array
    locations_list = []  # list of locations
    for i, location in enumerate(unique_locations, start=1):  # shows unique locations
        if flag:
            print(f"{i}. {location}")
        locations_list.append(location)
    return locations_list

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


# TODO: separate withdrawls from deposits & add hoverable amount labels
def plot_weekly_spending(df, start_date="02/01/2023", end_date="10/10/2023"):
    df["Transaction Date"] = pd.to_datetime(df["Transaction Date"], format="%m/%d/%Y")
    df["Net Amount"] = df.apply(  # creates new column for net spending
        lambda row: -row["Amount"] if row["Transaction Type"] == "W" else row["Amount"],
        axis=1,
    )
    weekly_spending = df.resample("W-MON", on="Transaction Date")["Net Amount"].sum()
    # convert dates to correct datetime object to limit graph
    start_date = pd.to_datetime(start_date, format="%m/%d/%Y")
    end_date = pd.to_datetime(end_date, format="%m/%d/%Y")
    plt.figure(figsize=(10, 6))

    plt.plot(weekly_spending.index, weekly_spending.values, marker="o", linestyle="-")
    plt.title("Weekly Spending")
    plt.xlabel("Ending Date")
    plt.ylabel("Net Change in Balance ($)")
    plt.grid(True)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.xlim(start_date, end_date)
    plt.show()


def plot_daily_spending(df, start_date="02/01/2023", end_date="09/01/2023"):
    df["Transaction Date"] = pd.to_datetime(df["Transaction Date"], format="%m/%d/%Y")
    df["Net Amount"] = (
        df.apply(  # add extra col for net amount to filter withdrawals from deposits
            lambda row: (
                -row["Amount"] if row["Transaction Type"] == "W" else row["Amount"]
            ),
            axis=1,
        )
    )
    print(df.head())
    daily_spending = df.resample("D", on="Transaction Date")["Net Amount"].sum()

    withdrawals = df[df["Net Amount"] < 0]
    deposits = df[df["Net Amount"] > 0]

    # convert dates to correct datetime object to limit graph
    start_date = pd.to_datetime(start_date, format="%m/%d/%Y")
    end_date = pd.to_datetime(end_date, format="%m/%d/%Y")

    plt.figure(figsize=(10, 6))

    # plt.plot(daily_spending.index, daily_spending.values, marker="o", linestyle="-")
    plt.plot(  # plot withdrawlls in red separately
        withdrawals["Transaction Date"],
        withdrawals["Net Amount"],
        marker="o",
        color="red",
        linestyle="-",
    )
    plt.plot(
        deposits["Transaction Date"],
        deposits["Net Amount"],
        marker="o",
        color="black",
        linestyle="-",
    )
    for _, row in df.iterrows():  # adds labels to points with amounts
        plt.text(
            row["Transaction Date"],
            row["Net Amount"],
            f"${abs(row['Net Amount']):,.2f}",
            ha="right",
            va="bottom",
        )
    plt.title("Daily Spending")
    plt.xlabel("Ending Date")
    plt.ylabel("Net Change in Balance ($)")
    plt.grid(True)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.xlim(start_date, end_date)
    plt.show()


def plot_bar_chart_of_withdrawals(locations, totals):
    # remove locations where transaction was deposit
    filtered_locations = [
        location for location, total in zip(locations, totals) if total != 0.0
    ]
    filtered_totals = [total for total in totals if total != 0.0]

    plt.figure(figsize=(10, 6))
    plt.bar(filtered_locations, filtered_totals, color="red")

    # Add labels and title
    plt.xlabel("Locations")
    plt.ylabel("Totals ($)")
    plt.title("Money Spent at All Locations")

    # Show plot
    plt.xticks(rotation=45)
    plt.tight_layout()  # Adjust layout
    plt.show()


def main():
    # Read the transaction.txt - dummy_transactions.txt for testing

    parser = argparse.ArgumentParser(description="Bank statement Analysis")
    parser.add_argument(
        "statement_path",
        help="Full path to the folder that contains your statement file as a .txt.",
    )
    # testing file path: "transactions/dummy_transactions.txt"
    args = parser.parse_args()
    transactions_file = open(args.statement_path, "r")
    transaction_lines = transactions_file.readlines()

    dates, locations, trans_types, amounts, balances = extract_categories(
        transaction_lines
    )

    print("-------------------------------------------------------------------------")
    df = create_dataframe(dates, locations, trans_types, amounts, balances)
    print(df.head(10))
    print("-------------------------------------------------------------------------")
    grandTotal = total_spent(df)
    print(f"Total spent over entire statement period: ${grandTotal}")
    
    print("-------------------------------------------------------------------------")
    
   
    main_actions = ["View Graphs", "View totals Over Date Range or Location", "Category 3"]
    selected_action = choose_option(main_actions)
    print(f"You selected: {selected_action}")
    print("-------------------------------------------------------------------------")
    printFlag=False
    all_locations = get_all_locations(df,printFlag)
    if selected_action == "View Graphs":
        sub_options = [
            "View Weekly Spending Graph",
            "View Daily Spending Graph",
            "View Total Spent By Location Graph",
        ]
  
    elif selected_action == "View totals Over Date Range or Location":
        sub_options = ['Total spent from specified start and end date', 'Total spent at given location']
       
    selected_suboptions = choose_option(sub_options)
   
    print(f"You selected: {selected_action}")
    if selected_suboptions == 'Total spent at given location':
        print("the unique locations>>>>>")
        printFlag = True
        all_locations= get_all_locations(df, printFlag)
        location_num = int(input("Choose an option from the locations: "))
        print("-------------------------------------------------------------------------")
        location_selected = all_locations[location_num - 1]
        print(
            f"Total at {location_selected}: ${"{:.2f}".format(total_spent_at_location(df, location_selected))}"
        )
        print("-------------------------------------------------------------------------")
    elif selected_suboptions == 'Total spent from specified start and end date':
        start_date = str(input("Enter a start date in the format MM/DD/YY: "))
        end_date = str(input("Enter an end date in the format MM/DD/YY: "))
        print(total_spent_over_date_range(df, start_date=start_date, end_date=end_date))
    
    elif selected_suboptions == 'View Weekly Spending Graph':
        plot_weekly_spending(df)
    elif selected_suboptions== 'View Daily Spending Graph':
        plot_daily_spending(df)
    else: #bar graph by locatioon 
        location_totals = []
        for location in all_locations:
            total = total_spent_at_location(df, location)
            location_totals.append(total)  # total for each location

        plot_bar_chart_of_withdrawals(all_locations, location_totals)


if __name__ == "__main__":
    main()
