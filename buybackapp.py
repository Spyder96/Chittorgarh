import os
import time
import tkinter as tk
from tkinter import ttk
from datetime import datetime
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
import requests

class BuybackAnalyzerApp:
    def __init__(self):
        url = 'https://www.chittorgarh.com/report/latest-buyback-issues-in-india/80/tender-offer-buyback/'
        Headers=({'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/111.0' , 'Accept-language':'en-US , en;q=0.5'})
        self.response = requests.get(url, headers=Headers)
        self.df = self._get_data()
        self.df = self._process_data()
        self._display_gui()

    
    def _get_data(self):
        if self.response.status_code == 200:
            tables = pd.read_html(self.response.text)
            desired_table = tables[2]
            return desired_table
        else:
            print(f"Failed to retrieve data. Status code: {self.response.status_code}")

    def _process_data(self):
        df = self.df
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
