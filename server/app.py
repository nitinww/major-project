from flask import Flask, jsonify, request
from flask_cors import CORS
import yfinance as yf
import tensorflow as tf
from sklearn.preprocessing import MinMaxScaler
import numpy as np

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "http://localhost:5173"}})


def add_technical_indicators(data):
    import pandas_ta as ta

    data["MA_5"] = ta.sma(data["Close"], length=5)
    data["MA_10"] = ta.sma(data["Close"], length=10)
    data["EMA_5"] = ta.ema(data["Close"], length=5)
    data["EMA_10"] = ta.ema(data["Close"], length=10)
    data["RSI"] = ta.rsi(data["Close"], length=14)

    return data


@app.route("/api/predict", methods=["POST"])
def get_data_and_prediction():
    try:
        ticker = request.json.get("ticker")
        print(f"Received ticker: {ticker}")

        data = yf.download(ticker, period="3mo", interval="1d")

        if data.empty:
            return jsonify(
                {"error": "Ticker not found. Please check the ticker symbol."}
            ), 404

        data = add_technical_indicators(data)

        data = data.tail(26)[:-1]

        data_json = data.reset_index().to_dict(orient="records")

        model = tf.keras.models.load_model("model.h5")

        scaler = MinMaxScaler()
        scaled_data = scaler.fit_transform(
            data[
                [
                    "Open",
                    "High",
                    "Low",
                    "Close",
                    "MA_5",
                    "MA_10",
                    "EMA_5",
                    "EMA_10",
                    "RSI",
                ]
            ]
        )

        x_input = scaled_data[:-1]
        print(f"Scaled input shape: {x_input.shape}")

        x_input = np.reshape(x_input, (1, x_input.shape[0], x_input.shape[1]))

        predicted = model.predict(x_input)

        predicted_candle = scaler.inverse_transform(predicted).tolist()

        return jsonify(
            {"received_data": data_json, "predicted_data": predicted_candle}
        ), 201

    except Exception as e:
        print(f"Error in get_data_and_prediction: {e}")
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True)
