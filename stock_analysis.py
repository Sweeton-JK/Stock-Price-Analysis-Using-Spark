import matplotlib
matplotlib.use('Agg')

from flask import Flask, render_template, request
from alpha_vantage.timeseries import TimeSeries
from pyspark.sql import SparkSession
import matplotlib.pyplot as plt
from io import BytesIO
import base64

app = Flask(__name__)

# Initialize Alpha Vantage API
api_key = 'TR9UZV9JUE6APDBB'
ts = TimeSeries(key=api_key, output_format='pandas')

# Initialize Spark
spark = SparkSession.builder.appName("StockAnalysis").getOrCreate()

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        # Get the selected stock symbol from the form
        selected_stock = request.form["stock_symbol"]

        # Fetch stock data from Alpha Vantage
        stock_data, meta_data = ts.get_daily(symbol=selected_stock, outputsize="compact")

        # Render the results in the web interface
        return render_template("index.html", stock_data=stock_data.to_html())

    # Render the initial form
    return render_template("index.html", stock_data=None, chart_data=None)

if __name__ == "__main__":
    app.run(debug=True)
