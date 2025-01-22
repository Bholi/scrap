import requests
import os
import pandas as pd
import json
from colorama import Fore, Style, init
from bs4 import BeautifulSoup
import time

url = "https://www.nepalstock.com/floor-sheet"

init(autoreset=True)

# Lists to hold the scraped data
SN = []
contract_no = []
stock_symbol = []
buyer = []
seller = []
quantity = []
rate = []
amount = []

def pd_columns() -> list:
    """Fetch the headers from the table on the floor sheet page."""
    res = requests.get(url).text
    souped_data = BeautifulSoup(res, 'html5lib')
    main_table = souped_data.find_all('table', attrs={'class': 'table table__lg table-striped table__border table__border--bottom'})[0]
    
    headers = []
    for th in main_table.find('thead').find_all('th'):
        headers.append(th.getText().strip())
    
    # Clean up headers if needed (remove empty or unwanted columns)
    headers = list(filter(lambda x: x != "", headers))
    return headers

def scrap():
    """Scrape the floor sheet data."""
    for page_indexing in range(1):  # You can adjust the range to loop through multiple pages if required.
        res = requests.get(url).content.decode('utf-8')
        souped_data = BeautifulSoup(res, 'html.parser')
        main_table = souped_data.find_all('table', {'class': 'table table__lg table-striped table__border table__border--bottom'})[0]
        
        # Extract table rows and scrape data
        for trs in main_table.find_all('tr')[1:]:  # Skipping the first row which is the header
            try:
                vals = trs.find_all('td')
                
                SN.append(vals[0].getText().strip())
                contract_no.append(vals[1].getText().strip())
                stock_symbol.append(vals[2].getText().strip())
                buyer.append(vals[3].getText().strip())
                seller.append(vals[4].getText().strip())
                quantity.append(vals[5].getText().strip())
                rate.append(vals[6].getText().strip())
                amount.append(vals[7].getText().strip())
                
                print(f'{Fore.GREEN}{Style.BRIGHT}[-]  {Fore.WHITE}{Style.BRIGHT}Stock Symbol: {vals[2].getText()}')
            except IndexError:
                break  # Stop if there's an issue parsing rows

def createCSV(file_name: str):
    """Create CSV file from scraped data."""
    titles = pd_columns()
    df = pd.DataFrame(columns=titles)
    
    df["SN"] = SN
    df["Contract No."] = contract_no
    df["Stock Symbol"] = stock_symbol
    df["Buyer"] = buyer
    df["Seller"] = seller
    df["Quantity"] = quantity
    df["Rate (Rs)"] = rate
    df["Amount (Rs)"] = amount
    
    df.to_csv(f"{file_name}.csv", index=False)
    print(f"File saved as {Fore.RED}{Style.BRIGHT}{file_name}.csv")

if __name__ == "__main__":
    scrap()
    
    yes_or_no = input("Do you want to save your file (y/n):  ")
    
    if yes_or_no.lower() == "y":
        file_name = input("Enter your file name: ")
        createCSV(file_name)
    else:
        print("Okay, exiting...")
        exit()
