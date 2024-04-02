import re
import pandas as pd
import os
from decimal import Decimal
import matplotlib.pyplot as plt
import argparse
import calendar

from transaction_report import create_analytics_report


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
def save_figure(type, filename=None):
    folder_path = 'graphs'

    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    filename =  filename if filename else f'{type}.png'
    full_path = os.path.join(folder_path, filename)
    plt.savefig(full_path)
    plt.close()
	


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


# TODO: add hoverable amount labels
def plot_weekly_spending(df, start_date=None,show=True):
    if start_date is None: #if it is null, the default is the beginning of statement
        start_date = pd.to_datetime(df['Transaction Date'].iloc[0])
      
    else:
        start_date = pd.to_datetime(start_date, format="%m/%d/%y")
        print('start date is: ', start_date, ' of type: ', type(start_date))
   
    print('type of start datte: ', type(start_date))
    tmp_end_date = start_date + pd.DateOffset(months=2) #2 months after start
    max_date_in_data = pd.to_datetime(df["Transaction Date"].iloc[-1])
    actual_end_date = min(tmp_end_date, max_date_in_data)
   
    df["Transaction Date"] = pd.to_datetime(df["Transaction Date"], format="%m/%d/%Y")
    date_filtered_df = df[(df["Transaction Date"] >= start_date) & (df["Transaction Date"] <= actual_end_date + pd.DateOffset(weeks=1))].copy()
    date_filtered_df["Net Amount"] = date_filtered_df.apply(  # creates new column for net spending
        lambda row: -row["Amount"] if row["Transaction Type"] == "W" else 0, #only considers withdrawal amounts
        axis=1,
    )
    weekly_spending = date_filtered_df.resample("W-MON", on="Transaction Date")["Net Amount"].sum()
    
    
    plt.figure(figsize=(10, 6))
    x= weekly_spending.index
    y=abs(weekly_spending.values)

    plt.plot(x, y, marker="o", linestyle="-")
    for date, amount in zip(weekly_spending.index, weekly_spending.values):
        plt.text(
            date,
            abs(amount),
            f"${abs(amount):,.2f}",
            ha="right",
            va="bottom",
            fontsize=8
        )
    start_date_str = start_date.date().strftime("%Y-%m-%d")
    plt.title(f"Weekly Spending Starting {start_date_str} ")
    plt.xlabel("Weeks")
    plt.ylabel("Amount Spent ($)")
    plt.grid(True)
    plt.xticks(rotation=45,fontsize=6)
    plt.tight_layout()
    plt.xlim(start_date, actual_end_date )
    if show:
        plt.show()
    else:
        save_figure('time series', 'Weekly_spending_plot')


#TODO: add legend for colors 
def plot_daily_transactions_by_type(df, start_date=None, show=True):
    df["Transaction Date"] = pd.to_datetime(df["Transaction Date"], format="%m/%d/%Y")
    df["Net Amount"] = (
        df.apply(  # add extra col for net amount to filter withdrawals from deposits
            lambda row: (
                -row["Amount"] if row["Transaction Type"] == "W" else row["Amount"]
            ),
            axis=1,
        )
    )
   
    daily_spending = df.resample("D", on="Transaction Date")["Net Amount"].sum()

    withdrawals = df[df["Net Amount"] < 0]
    deposits = df[df["Net Amount"] > 0]
  
    if start_date is None: #if it is null, the default is the beginning of statement
        start_date = df['Transaction Date'].iloc[0]
      
    else:
        start_date = pd.to_datetime(start_date, format="%m/%d/%y")
        print('start date is: ', start_date, ' of type: ', type(start_date))
   
    start_year = start_date.strftime('%Y')
    start_month_name =calendar.month_name[start_date.month]
    #30 day max (1 month) range from start:
    tmp_end_date = start_date + pd.DateOffset(months=1) 
    max_date_in_data = pd.to_datetime(df["Transaction Date"].iloc[-1])
    actual_end_date = min(tmp_end_date, max_date_in_data)
    unique_dates = pd.date_range(start=start_date, end=actual_end_date )
    
    plt.figure(figsize=(10, 6))

    
    plt.plot(  # plot withdrawals in red separately
        withdrawals["Transaction Date"],
        abs(withdrawals["Net Amount"]),
        marker="o",
        color="red",
        linestyle="-",
    )
    plt.plot(
        deposits["Transaction Date"],
        abs(deposits["Net Amount"]),
        marker="o",
        color="black",
        linestyle="-",
    )
    for _, row in withdrawals.iterrows():  # adds labels to points with amounts
        plt.text(
            row["Transaction Date"],
            abs(row["Net Amount"]),
            f"${abs(row['Net Amount']):,.2f}",
            ha="right",
            va="bottom",
            fontsize=8,
            bbox=dict(facecolor='white', alpha=0.5, pad=3) 
        )
    for _, row in deposits.iterrows():
        plt.text(
            row["Transaction Date"],
            abs(row["Net Amount"]),
            f"${abs(row['Net Amount']):,.2f}",
            ha="right",
            va="bottom",
            fontsize=8,
            bbox=dict(facecolor='white', alpha=0.5, pad=3)
        )
    plt.title(f"Daily Spending Starting {start_month_name} of {start_year}")
    plt.xlabel("Dates")
    plt.ylabel("Money Spent or Deposited($)")
    plt.grid(True)
    plt.xticks(unique_dates ,rotation=90, fontsize=6)
    plt.tight_layout()
    plt.xlim(start_date, actual_end_date )
    if show:
        plt.show()
    else:
        save_figure('time series', 'Daily_spending_by_type_plot')

def plot_bar_chart_of_withdrawals(df, start_date=None,show =True):
    if start_date is None: #if it is null, the default is the beginning of statement
        start_date = pd.to_datetime(df['Transaction Date'].iloc[0])
      
    else:
        start_date = pd.to_datetime(start_date, format="%m/%d/%y")

    tmp_end_date = start_date + pd.DateOffset(months=6) #6 months after start
    max_date_in_data = pd.to_datetime(df["Transaction Date"].iloc[-1])
    actual_end_date = min(tmp_end_date, max_date_in_data)
    #for graph title:
    start_month_name =calendar.month_name[start_date.month]
    end_month_name =calendar.month_name[actual_end_date.month]
  
    date_filtered_df = df[( pd.to_datetime(df["Transaction Date"]) >= start_date) & ( pd.to_datetime(df["Transaction Date"]) <= actual_end_date + pd.DateOffset(weeks=1))].copy()
    withdrawals_by_location = date_filtered_df[date_filtered_df["Transaction Type"] == 'W'].groupby("Location")["Amount"].sum() #group and sum location totals
    locations = withdrawals_by_location.index
    totals = withdrawals_by_location.values
    plt.figure(figsize=(10, 6))
    plt.bar(locations, totals, color="grey")

    # Add labels and title
    plt.xlabel("Locations")
    plt.ylabel("Totals ($)")
    plt.title(f"Money Spent at All Locations From {start_month_name} to {end_month_name}")

    # Show plot
    plt.xticks(rotation=45)
    plt.tight_layout()  # Adjust layout
    if show:
        plt.show()
    else:
        save_figure('bar chart', 'Spending_by_location_bar')



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
    main_actions = ["View Graphs", "View totals Over Date Range or Location", "Generate Report As PDF"]
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
    else: #generate report option
        sub_options = ['Create Report']


       
    selected_suboptions = choose_option(sub_options)
   
    print(f"You selected: {selected_suboptions}")
    #calculate location totals:
    location_totals = []
    for location in all_locations:
        total = total_spent_at_location(df, location)
        location_totals.append(total)  # total for each location
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
        total_in_range = total_spent_over_date_range(df, start_date=start_date, end_date=end_date)
        print( f"Total in that range: ${"{:.2f}".format(total_in_range)}")
    
    elif selected_suboptions == 'View Weekly Spending Graph':
        plot_weekly_spending(df)
    elif selected_suboptions== 'View Daily Spending Graph':
        plot_daily_transactions_by_type(df)
   
    elif selected_suboptions == 'Create Report':
        balance_end_date = df["Transaction Date"].iloc[-1]
        balance_start_date = df["Transaction Date"].iloc[0]
        current_balance = df["Balance"].iloc[-1]
      
        print('Do you want to choose a custom start date for report? (default is first transaction on statement)')
        binary_options = ['Yes', 'No']
        
        choice = choose_option(binary_options)
        if choice == 'Yes':
            start = str(input("Enter a start date in the format MM/DD/YY: ")) #TODO: Add valid date checks

        else:
            start = None

        plot_weekly_spending(df,start, show = False)
        plot_daily_transactions_by_type(df,start, show=False)
        plot_bar_chart_of_withdrawals(df, start, show=False)
       
        create_analytics_report(grandTotal,current_balance,balance_start_date, balance_end_date)
    elif selected_suboptions == 'View Total Spent By Location Graph': #bar graph by locatioon 
        print('bar chart selected: ')
        start = None
        plot_bar_chart_of_withdrawals(df,start, show=True)


if __name__ == "__main__":
    main()
