import os
import time
import tkinter as tk
from tkinter import ttk
from datetime import datetime
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By

class BuybackAnalyzerApp:
    def __init__(self):
        # Set up the WebDriver
        self.driver = webdriver.Chrome()
        self.download_dir = self._setup_download_dir()
        self.df = self._download_and_process_data()
        self._display_gui()

    def _setup_download_dir(self):
        user_home = os.path.expanduser("~")
        download_dir = os.path.join(user_home, "Downloads")
        return download_dir

    def _download_and_process_data(self):
        # Navigate to the web page
        self.driver.get('https://www.chittorgarh.com/report/latest-buyback-issues-in-india/80/tender-offer-buyback/')

        # Find the button element
        button = self.driver.find_element(By.ID, 'export_btn')

        # Execute JavaScript to trigger the download
        self.driver.execute_script("arguments[0].click();", button)

        # Wait for a few seconds to allow the download to start
        time.sleep(5)

        # Construct the file path
        sorted_file_list = self._get_sorted_file_list()
        if sorted_file_list[-1].endswith(".csv"):
            file_path = os.path.join(self.download_dir, sorted_file_list[-1])
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

            today = pd.to_datetime(datetime.today().date())
            df['Record Date Diff'] = (today - df['Record Date']).dt.days
            df['Apply Date Diff'] = (today - df['Issue Open']).dt.days
            df['Closed Date Diff'] = (today - df['Issue Close']).dt.days
            cdf = df[(df['Closed Date Diff'] <= 0 )]
            nadf = df[df['Closed Date Diff'].isna()]
            df = pd.concat([cdf, nadf], ignore_index = True)
            for col in date_columns:
                df[col]= pd.to_datetime(df[col]).dt.date

            df['Profit'] = df['BuyBack price (Per Share)'] - df['Current Market Price']
            minimum_price_difference = 100
            df = df[(df['Profit'] >= minimum_price_difference)]

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
            return df

    def _get_sorted_file_list(self):
        file_list = os.listdir(self.download_dir)
        return sorted(file_list, key=lambda x: os.path.getmtime(os.path.join(self.download_dir, x)))

    def _display_gui(self):
        # Create the main window
        root = tk.Tk()
        root.title("Buyback Analyzer")

        # Create a treeview widget for displaying the DataFrame
        treeview = ttk.Treeview(root, columns=list(self.df.columns), show="headings")
        column_names = self.df.columns.tolist()

        # Set column headings in the treeview
        for index, column in enumerate(column_names):
            treeview.heading(f"#{index+1}", text=column)

        # Insert DataFrame rows into the treeview with formatting
        for index, row in self.df.iterrows():
            formatted_values = []
            for value in row:
                if isinstance(value, (int, float)):
                    formatted_values.append("{:.2f}".format(value))
                else:
                    formatted_values.append(value)
            treeview.insert("", index, values=formatted_values)

        treeview.pack()

        # Start the tkinter main loop
        root.mainloop()

# Instantiate and run the app
app = BuybackAnalyzerApp()
