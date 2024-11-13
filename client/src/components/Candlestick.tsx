import { useState } from "react";
import axios from "axios";
import Chart from "react-apexcharts";
import { ApexOptions } from "apexcharts";

interface StockData {
  Date: string;
  Open: number;
  High: number;
  Low: number;
  Close: number;
}

interface ChartDataPoint {
  x: string;
  y: [number, number, number, number];
}

interface ChartData {
  series: {
    name: string;
    data: ChartDataPoint[];
  }[];
  options?: ApexOptions | undefined;
}

export default function Candlestick() {
  const [ticker, setTicker] = useState<string>("");
  const [responseData, setResponseData] = useState<StockData[] | null>(null);
  const [predictedData, setPredictedData] = useState<number[][] | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [chartData, setChartData] = useState<ChartData>({
    series: [
      {
        name: "Candlestick Data",
        data: [],
      },
    ],
    options: {
      chart: {
        type: "candlestick",
      },
      title: {
        text: "Stock Price Candlestick Chart",
        align: "center",
      },
      xaxis: {
        type: "category",
        labels: {
          formatter: function (value: string) {
            return new Date(value).toLocaleDateString();
          },
        },
      },
      yaxis: {
        tooltip: {
          enabled: true,
        },
      },
    },
  });

  const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setError(null);

    try {
      const response = await axios.post("http://127.0.0.1:5000/api/predict", {
        ticker: ticker,
      });

      const receivedData: StockData[] = response.data.received_data;
      const predictedData: number[][] = response.data.predicted_data;

      setResponseData(receivedData);
      setPredictedData(predictedData);
      updateChartData(receivedData);
    } catch (error: any) {
      setPredictedData(null);
      setResponseData(null);

      if (error.response && error.response.status === 404) {
        setError("Ticker not found. Please check the ticker symbol.");
      } else {
        setError("Error fetching predicted data. Please try again.");
      }
    }
  };

  const updateChartData = (data: StockData[]) => {
    const candlestickData: ChartDataPoint[] = data.map((entry) => ({
      x: entry.Date,
      y: [entry.Open, entry.High, entry.Low, entry.Close],
    }));

    setChartData((prevChartData) => ({
      ...prevChartData,
      series: [
        {
          name: "Candlestick Data",
          data: candlestickData,
        },
      ],
    }));
  };

  return (
    <div className="max-w-4xl mx-auto p-6 bg-gray-100 rounded-lg shadow-md">
      <form onSubmit={handleSubmit} className="flex justify-between mb-6">
        <input
          type="text"
          value={ticker}
          onChange={(e) => setTicker(e.target.value)}
          placeholder="Type ticker name..."
          className="flex-grow p-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
        <button
          type="submit"
          className="ml-4 px-4 py-2 text-white bg-blue-500 rounded-lg hover:bg-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-opacity-50"
        >
          Get Prediction
        </button>
      </form>

      {responseData && (
        <div className="mb-6">
          <h3 className="text-lg font-semibold mb-2">
            Stock Data Candlestick Chart:
          </h3>
          <Chart
            options={chartData.options}
            series={chartData.series}
            type="candlestick"
            height={600}
          />
        </div>
      )}

      {predictedData && (
        <div>
          <h3 className="text-lg font-semibold mb-2">
            Predicted Next Candle Data:
          </h3>
          <ul className="list-disc ml-5">
            <li>Low: {predictedData[0][2]}</li>
            <li>Open: {predictedData[0][0]}</li>
            <li>Close: {predictedData[0][3]}</li>
            <li>High: {predictedData[0][1]}</li>
          </ul>
        </div>
      )}

      {error && <p className="text-red-500">{error}</p>}
    </div>
  );
}
