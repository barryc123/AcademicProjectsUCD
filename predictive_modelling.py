"""
Functions that perform predictive modelling
"""
import pandas as pd
import yfinance as yf
from matplotlib import pyplot as plt
from prophet import Prophet
from sklearn.metrics import mean_absolute_error
import datetime as dt


def prophet_price_prediction(sentiment_df: pd.DataFrame, ratios_df: pd.DataFrame):
    # DataFrame that will be used at the end to hold our final stock picks
    final_stocks = pd.DataFrame(
        columns=['Ticker', 'P/E Ratio', 'P/B Ratio', 'Current Price', '1y Predicted Price', 'Price Increase (%)'])
    # Print the  number of stocks where more positive than negative sentiment
    positive_stocks_count = len(
        sentiment_df[sentiment_df['Positive'] > sentiment_df['Negative']].index)
    positive_stocks_tickers = list(
        sentiment_df[sentiment_df['Positive'] > sentiment_df['Negative']]['Stock'])
    print('There are ' + str(positive_stocks_count) + ' stocks with greater positive sentiment than negative.')
    print('They are: ' + str(positive_stocks_tickers))

    # Print the  number of stocks where more negative than positive sentiment
    negative_stocks_count = len(
        sentiment_df[sentiment_df['Positive'] < sentiment_df['Negative']].index)
    negative_stocks_tickers = list(
        sentiment_df[sentiment_df['Positive'] < sentiment_df['Negative']]['Stock'])
    print('There are ' + str(negative_stocks_count) + ' stocks with greater negative sentiment than positive.')
    print('They are: ' + str(negative_stocks_tickers))

    # We will only be using the stocks with positive sentiment
    # So filter this:
    predictions_df = sentiment_df[sentiment_df['Positive'] > sentiment_df['Negative']]
    predictions_df.reset_index(inplace=True, drop=True)

    # Tickers currently have dollar sign in them, need to remove it
    tickers_and_dollar = list(predictions_df['Stock'])
    tickers_no_dollar = []
    for ticker in tickers_and_dollar:
        ticker = ticker[1:]
        tickers_no_dollar.append(ticker)
    tickers = tickers_no_dollar

    # Prophet Model to predict prices
    for ticker in tickers:
        prices = yf.download(ticker, period="5y", interval='1d')
        prices['Date'] = prices.index

        data = prices[['Date', 'Adj Close']]
        data.rename(columns={'Date': 'ds', 'Adj Close': 'y'}, inplace=True)

        m = Prophet(daily_seasonality=True)
        m.fit(data)

        future = m.make_future_dataframe(periods=365)
        prediction = m.predict(future)
        m.plot(prediction)

        plt.title("Prediction of " + ticker + " Stock Price")
        plt.xlabel("Date")
        plt.ylabel("Stock Price")
        plt.legend(labels=['Actual Price', "Predicted Price"])
        plt.show()

        # Check if price is predicted to increase
        current_price = float(prediction['trend'][-366:-365].round(2))
        predicted_price = float(prediction['trend'][-1:].round(2))
        if predicted_price > current_price:
            ticker = ticker
            ticker_pe = ratios_df['PE'].loc[ticker]
            ticker_pb = ratios_df['PB'].loc[ticker]
            current_price = current_price
            predicted_price = predicted_price
            price_increase = round((((predicted_price - current_price) / current_price) * 100), 2)

            # If the price of the stock is predicted to increase, add it to the final dataframe
            final_stocks.loc[final_stocks.shape[0]] = (ticker, ticker_pe, ticker_pb, current_price, predicted_price, price_increase)

            # ----------------
            # Now Testing the Model  on our chosen stocks
            # Test the model on last 12 months of data - see if it would be accurate historically
            # Train on first 4 years, test on last year
            # Create the test dataset, remove last 252 days prices
            train = data.drop(data.index[-252:])

            # define the model
            model = Prophet()
            # fit the model
            model.fit(train)

            # Define the period for which we want a prediction - the last year in this case
            future = data.iloc[-252:]
            # Use the model to make a forecast
            forecast = model.predict(future)

            # Calculate MAE between expected and predicted values
            y_true = data['y'][-252:].values
            y_pred = forecast['yhat'].values
            mae = mean_absolute_error(y_true, y_pred)
            print('Model MAE: ' + str(mae))
            # Mean Absolute Error means the predicted price is approx X dollars off the actual price

            # Compute the accuracy score
            # from sklearn.metrics import accuracy_score
            # accuracy = accuracy_score(y_true, y_pred, normalize=False)
            # print(accuracy)

            # Plot the Model
            # Need to format dates
            dates = list((data['ds'][-252:]))
            format_dates = []
            for date in dates:
                date = date.strftime('%d/%m/%Y')
                format_dates.append(date)
            x = [dt.datetime.strptime(d, '%d/%m/%Y').date() for d in format_dates]

            plt.plot(x, y_true, label='Actual', color='black')
            plt.plot(x, y_pred, label='Predicted', color='steelblue')
            plt.title(ticker + ' Price Prediction Model - Last 12 months \n Mean Absolute Error: ' + str(mae.round(2)))
            plt.ylabel('Stock Price')
            plt.xlabel('Date')
            plt.gcf().autofmt_xdate()
            plt.legend()
            plt.tight_layout()
            plt.show()
        else:
            pass

    pass