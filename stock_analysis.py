from flask import Flask, render_template, request
from alpha_vantage.timeseries import TimeSeries
from pyspark.sql import SparkSession

app = Flask(__name__)

api_key = 'YOUR_ALPHA_VANTAGE_API_KEY'
ts = TimeSeries(key=api_key, output_format='pandas')

spark = SparkSession.builder.appName("StockAnalysis").getOrCreate()

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        selected_stock = request.form["stock_symbol"]

        stock_data, meta_data = ts.get_daily(symbol=selected_stock, outputsize="compact")

        return render_template("index.html", stock_data=stock_data.to_html())

    return render_template("index.html", stock_data=None)

if __name__ == "__main__":
    app.run(debug=True)
