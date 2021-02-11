import sys
from flask import Flask, jsonify, request
from flask_cors import CORS
from datetime import datetime

from ticker_counts import main as update_reddit_mentions
from yfinance_analysis import main as update_financial_data

import csv
import os.path
import pandas as pd


app = Flask(__name__)
cors = CORS(app)

@app.route('/get-basic-data', methods=['GET'])
def get_basic_data() -> str:
	data_directory = "./data"
	date_created = datetime.today().strftime('%Y-%m-%d')
	mentions_filename = f"{data_directory}/{date_created}_tick_df.csv"
	financial_filename = f"{data_directory}/{date_created}_financial_df.csv"

	if not os.path.exists(mentions_filename):
		update_reddit_mentions()

	if not os.path.exists(financial_filename):
		update_financial_data()

	mentions_df = pd.read_csv(f"{mentions_filename}")
	financial_df = pd.read_csv(f"{financial_filename}")

	combined_df = financial_df.join(mentions_df.set_index('Ticker'), on='Ticker')
	combined_df.sort_values(by=["Mentions"], inplace=True, ascending=False)

	items_per_page = 10
	page = 1
	page_str = request.args.get('page')
	if page_str is not None:
		page = int(page_str) if (int(page_str) > 0) else 1

	first_idx = (page-1)*items_per_page

	return combined_df.iloc[first_idx:first_idx+items_per_page].to_json(orient = "records")
