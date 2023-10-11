import matplotlib
matplotlib.use('Agg')


from flask import Flask, render_template, request, send_file
from alpha_vantage.timeseries import TimeSeries
from sklearn.linear_model import LinearRegression
from io import BytesIO
import pandas as pd
import matplotlib.pyplot as plt
import base64

app = Flask(__name__)

# Initialize Alpha Vantage API
api_key = 'TR9UZV9JUE6APDBB'
ts = TimeSeries(key=api_key, output_format='pandas')

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        # Get the selected stock symbol from the form
        selected_stock = request.form["stock_symbol"]

        # Fetch stock data from Alpha Vantage
        stock_data, meta_data = ts.get_daily(symbol=selected_stock, outputsize="compact")
        if request.form.get("predict_price"):
            # Fetch historical stock data
            stock_data, _ = ts.get_daily(symbol=selected_stock, outputsize="full")

            # Extract closing price and date
            stock_data = stock_data[['4. close']]
            stock_data.reset_index(inplace=True)

            # Convert the date to a numerical format (e.g., Unix timestamp)
            stock_data['date'] = stock_data['date'].astype('datetime64[ns]').view('int64') // 10**9

            # Train a linear regression model
            X = stock_data[['date']]
            y = stock_data['4. close']
            model = LinearRegression()
            model.fit(X, y)

            # Convert the selected date to the same format
            selected_date = pd.Timestamp(request.form["selected_date"]).value // 10**9

            # Predict the stock price for the selected date
            predicted_price = model.predict([[selected_date]])[0]

            # Render the prediction result
            return render_template("index.html", predicted_price=predicted_price)

        if request.form.get("plot_graph"):  # Check if the plot_graph button was clicked
            # Create a Matplotlib graph with the closing price
            plt.figure(figsize=(10, 5))
            plt.plot(stock_data.index, stock_data['4. close'], label='Closing Price')
            plt.xlabel('Date')
            plt.ylabel('Price')
            plt.title(f'{selected_stock} Closing Price')
            plt.legend()
            
            # Save the graph to a BytesIO object
            graph = BytesIO()
            plt.savefig(graph, format='png')
            graph.seek(0)

            graph_base64 = base64.b64encode(graph.read()).decode('utf-8')

            # Render the results with the graph
            return render_template("index.html", stock_data=stock_data.to_html(), graph_base64=graph_base64)

        # Render the results without the graph
        return render_template("index.html", stock_data=stock_data.to_html(), graph=None)

    # Render the initial form
    return render_template("index.html", stock_data=None, graph_base64=None)

if __name__ == "__main__":
    app.run(debug=True, port=5001)
