# Validation MAE: 0.03380599131945474
# Validation MSE: 0.0025196285177800093
# Training Loss: 0.00082260638009756

import yfinance as yf
import numpy as np
import pandas_ta as ta
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, GRU, Dropout
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_absolute_error, mean_squared_error

def fib(n):
    # fibonaacci sequence code

def add_technical_indicators(data):
    data["MA_5"] = ta.sma(data["Close"], length=5)
    data["MA_10"] = ta.sma(data["Close"], length=10)
    data["EMA_5"] = ta.ema(data["Close"], length=5)
    data["EMA_10"] = ta.ema(data["Close"], length=10)
    data["RSI"] = ta.rsi(data["Close"], length=14)

    data.dropna(inplace=True)

    return data


def create_model(ticker):
    data = yf.download(ticker, start="2010-01-01", end="2022-02-26")
    data.reset_index(inplace=True)

    data = add_technical_indicators(data)

    scaler = MinMaxScaler()
    scaled_data = scaler.fit_transform(
        data[
            ["Open", "High", "Low", "Close", "MA_5", "MA_10", "EMA_5", "EMA_10", "RSI"]
        ]
    )

    x_data = []
    y_data = []
    for i in range(24, len(scaled_data)):
        x_data.append(scaled_data[i - 24 : i])
        y_data.append(scaled_data[i])

    x_data, y_data = np.array(x_data), np.array(y_data)
    x_data = np.reshape(x_data, (x_data.shape[0], x_data.shape[1], x_data.shape[2]))

    train_size = int(len(x_data) * 0.8)
    x_train, x_val = x_data[:train_size], x_data[train_size:]
    y_train, y_val = y_data[:train_size], y_data[train_size:]

    model = Sequential()
    model.add(
        GRU(
            100, return_sequences=True, input_shape=(x_train.shape[1], x_train.shape[2])
        )
    )
    model.add(Dropout(0.3))
    model.add(GRU(100, return_sequences=False))
    model.add(Dropout(0.3))
    model.add(Dense(50))
    model.add(Dense(9))

    model.compile(optimizer="adam", loss="mean_squared_error")

    history = model.fit(
        x_train, y_train, batch_size=16, epochs=50, validation_data=(x_val, y_val)
    )

    model.save("model.h5")

    predicted_val = model.predict(x_val)

    mae = mean_absolute_error(y_val, predicted_val)
    mse = mean_squared_error(y_val, predicted_val)

    print(f"Validation MAE: {mae}")
    print(f"Validation MSE: {mse}")
    print(f"Training Loss: {history.history['loss'][-1]}")


create_model("^NSEI")
