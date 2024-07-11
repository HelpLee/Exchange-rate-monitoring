import requests
from bs4 import BeautifulSoup
import time
import pandas as pd
from datetime import datetime
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from smtplib import SMTP_SSL
import threading

# Define the CSV file path
csv_file = 'euro_exchange_rates.csv'

# Email configuration
smtp_server = 'smtp.qq.com'  # SMTP server for QQ Mail
smtp_port = 465  # SMTP port for SSL/TLS
smtp_user = '1067520491@qq.com'  # Your QQ email address (sender)
smtp_password = 'snazyhqabsdbbbii'  # Your QQ email authorization code (password)
recipient_emails = ['lee.heyboy@gmail.com']  # List of recipient email addresses

# Threshold values
forex_buy_threshold = 788.5  # High threshold for forex buy price
forex_sell_threshold = 720.0  # Low threshold for forex sell price

def send_email(subject, body, recipients):
    """
    Sends an email with the given subject and body to multiple recipients.
    """
    msg = MIMEMultipart()
    msg['From'] = smtp_user
    msg['To'] = ', '.join(recipients)  # Join recipient emails into a single string for the email header
    msg['Subject'] = subject

    msg.attach(MIMEText(body, 'plain'))

    try:
        # Use SMTP_SSL to connect to the SMTP server with SSL
        server = SMTP_SSL(smtp_server, smtp_port)
        server.set_debuglevel(0)  # Disable debug output
        server.login(smtp_user, smtp_password)
        text = msg.as_string()
        server.sendmail(smtp_user, recipients, text)  # Send email to a list of recipients
        server.quit()
        print("Email sent successfully")
    except Exception as e:
        print(f"Failed to send email: {e}")

def scrape_euro_data():
    """
    Scrapes the Euro exchange rate data from the Bank of China website.
    """
    # URL of the Bank of China's exchange rate page
    url = 'https://www.boc.cn/sourcedb/whpj/'
    
    try:
        # Send a GET request to the webpage with a timeout of 10 seconds
        response = requests.get(url, timeout=10)
        response.encoding = 'utf-8'  # Ensure the correct encoding

        # Parse the HTML content using BeautifulSoup
        soup = BeautifulSoup(response.text, 'html.parser')

        # Find the table containing the currency data
        table = soup.find('table', {'cellpadding': '0', 'align': 'left', 'cellspacing': '0', 'width': '100%'})

        # Check if the table was found
        if table:
            # Find all rows in the table
            rows = table.find_all('tr')

            # Iterate through the rows to find the one containing '欧元' (Euro)
            for row in rows:
                cells = row.find_all('td')
                if cells and cells[0].text.strip() == '欧元':
                    # Extract the data from the table row
                    forex_buy_price = float(cells[1].text.strip())
                    cash_buy_price = float(cells[2].text.strip())
                    forex_sell_price = float(cells[3].text.strip())
                    cash_sell_price = float(cells[4].text.strip())
                    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

                    # Print the extracted data
                    print(f"Timestamp: {timestamp}, Forex Buy Price: {forex_buy_price}, Cash Buy Price: {cash_buy_price}, Forex Sell Price: {forex_sell_price}, Cash Sell Price: {cash_sell_price}")

                    # Check thresholds and send email if needed
                    if forex_buy_price > forex_buy_threshold:
                        subject = f"Forex Buy Price Alert: {forex_buy_price}"
                        body = (f"Timestamp: {timestamp}\n"
                                f"The following are bank perspectives,taking the purchasing power of 100 euros against the Chinese yuan as an example::\n"
                                f"Forex Buy Price: {forex_buy_price}--The best time to exchange Euros to Chinese Yuan!\n"
                                f"Cash Buy Price: {cash_buy_price}\n"
                                f"Forex Sell Price: {forex_sell_price}\n"
                                f"Cash Sell Price: {cash_sell_price}\n"
                                f"---Chinese version below---\n"
                                f"时间戳: {timestamp}\n"
                                f"以下是银行视角，以100欧元兑换人民币的购买力为例:\n"
                                f"外汇买入价: {forex_buy_price}--兑换欧元为人民币的最佳时机！\n"
                                f"现钞买入价: {cash_buy_price}\n"
                                f"外汇卖出价: {forex_sell_price}\n"
                                f"现钞卖出价: {cash_sell_price}")
                        email_thread = threading.Thread(target=send_email, args=(subject, body, recipient_emails))
                        email_thread.start()

                    if forex_sell_price < forex_sell_threshold:
                        subject = f"Forex Sell Price Alert: {forex_sell_price}"
                        body = (f"Timestamp: {timestamp}\n"
                                f"The following are bank perspectives,taking the purchasing power of 100 euros against the Chinese yuan as an example::\n"
                                f"Forex Buy Price: {forex_buy_price}\n"
                                f"Cash Buy Price: {cash_buy_price}\n"
                                f"Forex Sell Price: {forex_sell_price}--The best time to exchange Chinese Yuan to Euros!\n"
                                f"Cash Sell Price: {cash_sell_price}\n"
                                f"---Chinese version below---\n"
                                f"时间戳: {timestamp}\n"
                                f"以下是银行视角，以100欧元兑换人民币的购买力为例:\n"
                                f"外汇买入价: {forex_buy_price}\n"
                                f"现钞买入价: {cash_buy_price}\n"
                                f"外汇卖出价: {forex_sell_price}--兑换人民币为欧元的最佳时机！\n"
                                f"现钞卖出价: {cash_sell_price}")


                        email_thread = threading.Thread(target=send_email, args=(subject, body, recipient_emails))
                        email_thread.start()

                    # Append the data to the CSV file
                    append_thread = threading.Thread(target=append_to_csv, args=(timestamp, forex_buy_price, cash_buy_price, forex_sell_price, cash_sell_price))
                    append_thread.start()
                    break
            else:
                print("Euro data not found.")
        else:
            print("Table not found.")
    except requests.exceptions.Timeout:
        print("The request timed out.")
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")

def append_to_csv(timestamp, forex_buy_price, cash_buy_price, forex_sell_price, cash_sell_price):
    """
    Appends the new data to the CSV file.
    """
    # Create a DataFrame with the new data
    new_data = pd.DataFrame({
        'Timestamp': [timestamp],
        'Forex Buy Price': [forex_buy_price],
        'Cash Buy Price': [cash_buy_price],
        'Forex Sell Price': [forex_sell_price],
        'Cash Sell Price': [cash_sell_price]
    })

    # Append the new data to the CSV file
    if not os.path.isfile(csv_file):
        new_data.to_csv(csv_file, index=False)
    else:
        new_data.to_csv(csv_file, mode='a', header=False, index=False)

# Run the scrape function every 5 minutes
while True:
    scrape_euro_data()
    time.sleep(300)  # Sleep for 300 seconds (5 minutes)
