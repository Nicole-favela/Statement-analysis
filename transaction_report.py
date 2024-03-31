from fpdf import FPDF
from datetime import datetime, timedelta
import os


WIDTH = 210
HEIGHT = 297
CREATION_DATE = datetime.today().date()  # todays date


def create_title(pdf, date):
    pdf.set_font("Arial", "", 24)
    pdf.ln(20)  # create line break
    pdf.write(5, f"Statement Report")
    pdf.ln(10)
    pdf.set_font("Arial", "", 16)
    pdf.write(4, f"Created: {date}")
    pdf.ln(5)


def create_analytics_report(
    total_spent,
    current_balance,
    balance_start_date,
    balance_end_date,
    date=CREATION_DATE,
    filename="statement_report.pdf",
):
    print("the end date is: ", balance_end_date)
    pdf = FPDF()  # A4
    # first page
    pdf.add_page()
    create_title(pdf, date)
    # subheading of report
    pdf.set_font("Arial", "", 12)
    pdf.ln(2)
    # pdf.write(5, f"Total spent: ${total_spent}")
    pdf.write(5, f"Statement date range: {balance_start_date}-{balance_end_date}")
    pdf.ln(5)
    pdf.write(5, f"Current balance: ${current_balance} as of {balance_end_date}")
    pdf.ln(3)
    # add graphs:
    pdf.image("./graphs/Spending_by_location_bar.png", 5, 60, WIDTH - 20)
    pdf.ln(3)
    pdf.image("./graphs/Weekly_spending_plot.png", 5, 180, WIDTH / 2 - 10)
    pdf.ln(3)
    pdf.image(
        "./graphs/Daily_spending_by_type_plot.png", WIDTH / 2, 180, WIDTH / 2 - 10
    )

    pdf.output(filename)
