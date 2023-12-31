from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import os
from datetime import datetime
import pandas as pd
import numpy as np
# Set up the WebDriver
driver = webdriver.Chrome()

# Navigate to the web page
driver.get('https://www.chittorgarh.com/report/latest-buyback-issues-in-india/80/tender-offer-buyback/')

# Find the button element
button = driver.find_element(By.ID, 'export_btn')

# Execute JavaScript to trigger the download
driver.execute_script("arguments[0].click();", button)

# Wait for a few seconds to allow the download to start
time.sleep(5)

# Close the WebDriver
driver.quit()
#Get the user's home directory
user_home = os.path.expanduser("~")

# Construct the download directory path
download_dir = os.path.join(user_home, "Downloads")
# Get a list of filenames in the directory
file_list = os.listdir(download_dir)
# Sort the file list based on date modified

sorted_file_list = sorted(file_list, key=lambda x: os.path.getmtime(os.path.join(download_dir, x)))

# # Print the sorted list of filenames
# for filename in sorted_file_list:
#     file_path = os.path.join(download_dir, filename)
#     modified_time = os.path.getmtime(file_path)
#     # Format the modification timestamp
#     formatted_time = datetime.fromtimestamp(modified_time).strftime('%d-%m-%Y %H:%M:%S')
#     print(f"{filename} - Last Modified: {formatted_time}")
if sorted_file_list[-1].endswith(".csv"):
    file_path = os.path.join(download_dir, sorted_file_list[-1])
    df = pd.read_csv(file_path)

date_columns=['Record Date', 'Issue Open', 'Issue Close']
# Format string to match the input date format
date_input_format = "%b %d, %Y"
for col in date_columns:
    df[col]= pd.to_datetime(df[col], format = date_input_format)
df = df[['Company Name', 'Record Date', 'Issue Open', 'Issue Close',
        'BuyBack price (Per Share)', 'Current Market Price',
       'Issue Size - Shares (Cr)', 'Issue Size - Amount (Cr)']]
df = df.dropna(subset=['Record Date'])
today = datetime.today()      #.strftime('%Y-%m-%d')

df['Record Date Diff'] = (today - df['Record Date']).dt.days
df['Apply Date Diff'] = (today - df['Issue Open']).dt.days
df['Closed Date Diff'] = (today - df['Issue Close']).dt.days
cdf = df[(df['Closed Date Diff'] <= 0 )]
nadf = df[df['Closed Date Diff'].isna()]
df = pd.concat([cdf, nadf], ignore_index = True)
for col in date_columns:
    df[col]= pd.to_datetime(df[col]).dt.date

df['Profit']= df['BuyBack price (Per Share)'] - df['Current Market Price']
minimum_price_difference = 100
df = df[(df['Profit'] >= minimum_price_difference )]

df = df[['Company Name', 'Record Date', 'Issue Open', 'Issue Close', 'Profit',
       'Issue Size - Shares (Cr)', 'Issue Size - Amount (Cr)', 'BuyBack price (Per Share)', 'Current Market Price']]

try:
    # Delete the file
    os.remove(file_path)
    print(f"File '{file_path}' has been deleted.")
except FileNotFoundError:
    print(f"File '{file_path}' not found.")
except Exception as e:
    print(f"An error occurred: {e}")

import tkinter as tk
from tkinter import ttk
import pandas as pd


# Create the main window
root = tk.Tk()
root.title("DataFrame Display")

# Create a treeview widget for displaying the DataFrame
treeview = ttk.Treeview(root, columns=list(df.columns), show="headings")
column_names = df.columns.tolist()

# Set column headings in the treeview
for index, column in enumerate(column_names):
    treeview.heading(f"#{index+1}", text=column)

# Insert DataFrame rows into the treeview
for index, row in df.iterrows():
    formatted_values = []
    for value in row:
        if isinstance(value, (int, float)):
            formatted_values.append("{:.2f}".format(value))
        else:
            formatted_values.append(value)
    treeview.insert("", index, values=formatted_values)
    #treeview.insert("", index, values=row.tolist())

treeview.pack()

# Start the tkinter main loop
root.mainloop()
