from flask import Flask, render_template, request, redirect, url_for, jsonify
import pandas as pd
import numpy as np
import yfinance as yf
from keras.models import load_model
from sklearn.preprocessing import MinMaxScaler
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import io
import base64
import os
from datetime import datetime

matplotlib.use('Agg')

app = Flask(__name__)

BASE_DIR   = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "model.keras")
model = load_model(MODEL_PATH)

POPULAR_CRYPTOS = [
    {"symbol": "BTC-USD", "name": "Bitcoin",  "icon": "₿"},
    {"symbol": "ETH-USD", "name": "Ethereum", "icon": "Ξ"},
    {"symbol": "BNB-USD", "name": "BNB",      "icon": "B"},
    {"symbol": "SOL-USD", "name": "Solana",   "icon": "◎"},
    {"symbol": "ADA-USD", "name": "Cardano",  "icon": "₳"},
    {"symbol": "XRP-USD", "name": "XRP",      "icon": "✕"},
]

# ── Dark theme style for all matplotlib plots ─────────────────────────────────
PLOT_STYLE = {
    "figure.facecolor":  "#0d1117",
    "axes.facecolor":    "#0d1117",
    "axes.edgecolor":    "#30363d",
    "axes.labelcolor":   "#8b949e",
    "axes.titlecolor":   "#e6edf3",
    "xtick.color":       "#8b949e",
    "ytick.color":       "#8b949e",
    "grid.color":        "#21262d",
    "legend.facecolor":  "#161b22",
    "legend.edgecolor":  "#30363d",
    "legend.labelcolor": "#c9d1d9",
    "text.color":        "#c9d1d9",
}

def apply_dark_style():
    plt.rcParams.update(PLOT_STYLE)

def plot_to_html(fig):
    buf = io.BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight", dpi=120)
    buf.seek(0)
    data = base64.b64encode(buf.getbuffer()).decode("ascii")
    buf.close()
    plt.close(fig)
    return f"data:image/png;base64,{data}"

def fetch_stock(ticker):
    end   = datetime.now()
    start = datetime(end.year - 10, end.month, end.day)
    data  = yf.download(ticker, start=start, end=end, progress=False, auto_adjust=True)
    if isinstance(data.columns, pd.MultiIndex):
        data.columns = data.columns.get_level_values(0)
    return data

# ── Live USD → INR exchange rate ──────────────────────────────────────────────
_inr_cache = {"rate": None, "ts": None}

def get_usd_to_inr():
    """Return live USD→INR rate, cached for 5 minutes."""
    now = datetime.now()
    if _inr_cache["rate"] and _inr_cache["ts"] and (now - _inr_cache["ts"]).seconds < 300:
        return _inr_cache["rate"]
    try:
        fx   = yf.Ticker("USDINR=X")
        hist = fx.history(period="1d")
        rate = float(hist["Close"].iloc[-1]) if not hist.empty else 84.0
    except Exception:
        rate = 84.0   # sensible fallback
    _inr_cache["rate"] = rate
    _inr_cache["ts"]   = now
    return rate

def to_inr(usd_value, rate):
    return round(usd_value * rate, 2)

def fmt_inr(value):
    """Format number in Indian numbering system with ₹ prefix."""
    value = round(value, 2)
    s = f"{value:,.2f}"
    # Convert Western commas to Indian lakh/crore style
    parts = s.split(".")
    integer = parts[0].replace(",", "")
    decimals = parts[1]
    if len(integer) > 3:
        last3 = integer[-3:]
        rest  = integer[:-3]
        groups = []
        while len(rest) > 2:
            groups.insert(0, rest[-2:])
            rest = rest[:-2]
        if rest:
            groups.insert(0, rest)
        integer = ",".join(groups) + "," + last3
    return f"₹{integer}.{decimals}"

# ── API: Live prices ──────────────────────────────────────────────────────────
@app.route("/api/live-prices")
def live_prices():
    results = []
    for c in POPULAR_CRYPTOS:
        try:
            ticker = yf.Ticker(c["symbol"])
            hist   = ticker.history(period="2d")
            if len(hist) >= 2:
                prev  = float(hist["Close"].iloc[-2])
                curr  = float(hist["Close"].iloc[-1])
                chg   = ((curr - prev) / prev) * 100
            elif len(hist) == 1:
                curr = float(hist["Close"].iloc[-1])
                chg  = 0.0
            else:
                continue
            inr_rate = get_usd_to_inr()
            results.append({
                "symbol":    c["symbol"],
                "name":      c["name"],
                "icon":      c["icon"],
                "price_usd": round(curr, 2),
                "price_inr": round(curr * inr_rate, 2),
                "change":    round(chg, 2),
            })
        except Exception:
            pass
    return jsonify(results)

# ── API: Comparison data ──────────────────────────────────────────────────────
@app.route("/api/compare")
def compare():
    symbols = request.args.getlist("symbols")
    symbols = [s.strip().upper() for s in symbols if s.strip()][:3]
    if not symbols:
        return jsonify({"error": "No symbols provided"}), 400

    COLORS = ["#f7931a", "#627eea", "#00d4aa"]
    datasets = []
    for i, sym in enumerate(symbols):
        try:
            end   = datetime.now()
            start = datetime(end.year - 1, end.month, end.day)
            data  = yf.download(sym, start=start, end=end, progress=False, auto_adjust=True)
            if isinstance(data.columns, pd.MultiIndex):
                data.columns = data.columns.get_level_values(0)
            if data.empty:
                continue
            # Normalise to % change from start
            close  = data["Close"].dropna()
            normed = ((close / close.iloc[0]) - 1) * 100
            datasets.append({
                "symbol": sym,
                "dates":  [d.strftime("%Y-%m-%d") for d in normed.index],
                "values": [round(v, 2) for v in normed.tolist()],
                "color":  COLORS[i % len(COLORS)],
            })
        except Exception:
            pass
    return jsonify(datasets)

# ── Routes ────────────────────────────────────────────────────────────────────
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        stock      = request.form.get("stock", "BTC-USD").strip().upper()
        no_of_days = request.form.get("no_of_days", "10")
        try:
            no_of_days = int(no_of_days)
            if no_of_days < 1 or no_of_days > 100:
                raise ValueError
        except ValueError:
            return render_template("index.html", error="Please enter a number between 1 and 100.",
                                   popular_cryptos=POPULAR_CRYPTOS)
        return redirect(url_for("predict", stock=stock, no_of_days=no_of_days))
    return render_template("index.html", popular_cryptos=POPULAR_CRYPTOS)


@app.route("/predict")
def predict():
    stock      = request.args.get("stock", "BTC-USD")
    no_of_days = request.args.get("no_of_days", "10")
    try:
        no_of_days = int(no_of_days)
    except ValueError:
        no_of_days = 10

    try:
        stock_data = fetch_stock(stock)
    except Exception as e:
        return render_template("result.html", error=f"Failed to fetch data: {str(e)}", stock=stock)

    if stock_data.empty:
        return render_template("result.html", error=f"No data found for '{stock}'. Check the ticker symbol.", stock=stock)

    if len(stock_data) < 120:
        return render_template("result.html", error="Not enough historical data. Try a more established ticker.", stock=stock)

    # ── Data Preparation ──────────────────────────────────────────────────────
    splitting_len = int(len(stock_data) * 0.9)
    x_test        = stock_data[["Close"]][splitting_len:]

    scaler      = MinMaxScaler(feature_range=(0, 1))
    scaled_data = scaler.fit_transform(x_test)

    x_data, y_data = [], []
    for i in range(100, len(scaled_data)):
        x_data.append(scaled_data[i - 100:i])
        y_data.append(scaled_data[i])

    if not x_data:
        return render_template("result.html", error="Not enough test data for predictions.", stock=stock)

    x_data = np.array(x_data)
    y_data = np.array(y_data)

    predictions     = model.predict(x_data, verbose=0)
    inv_predictions = scaler.inverse_transform(predictions)
    inv_y_test      = scaler.inverse_transform(y_data)

    plotting_data = pd.DataFrame({
        "Original Test Data":  inv_y_test.flatten(),
        "Predicted Test Data": inv_predictions.flatten(),
    }, index=x_test.index[100:])

    apply_dark_style()

    # ── Plot 1: Original Closing Prices ───────────────────────────────────────
    fig1, ax1 = plt.subplots(figsize=(14, 5))
    ax1.plot(stock_data["Close"], color="#f7931a", linewidth=1.2, label="Close Price")
    ax1.fill_between(stock_data.index, stock_data["Close"], alpha=0.08, color="#f7931a")
    ax1.set_title(f"{stock}  ·  Historical Closing Prices", fontsize=13, pad=12)
    ax1.set_xlabel("Date"); ax1.set_ylabel("Price (20b9 INR)")
    ax1.xaxis.set_major_formatter(mdates.DateFormatter("%b '%y"))
    ax1.xaxis.set_major_locator(mdates.MonthLocator(interval=12))
    ax1.grid(alpha=0.25, linestyle="--")
    ax1.legend()
    fig1.tight_layout()
    original_plot = plot_to_html(fig1)

    # ── Plot 2: Original vs Predicted ─────────────────────────────────────────
    fig2, ax2 = plt.subplots(figsize=(14, 5))
    ax2.plot(plotting_data["Original Test Data"],  color="#58a6ff", linewidth=1.4, label="Actual")
    ax2.plot(plotting_data["Predicted Test Data"], color="#3fb950", linewidth=1.4,
             linestyle="--", label="Predicted", alpha=0.9)
    ax2.set_title(f"{stock}  ·  Actual vs Predicted", fontsize=13, pad=12)
    ax2.set_xlabel("Date"); ax2.set_ylabel("Price (20b9 INR)")
    ax2.xaxis.set_major_formatter(mdates.DateFormatter("%b '%y"))
    ax2.grid(alpha=0.25, linestyle="--")
    ax2.legend()
    fig2.tight_layout()
    predicted_plot = plot_to_html(fig2)

    # ── Plot 3: Future Predictions ────────────────────────────────────────────
    last_100        = stock_data[["Close"]].tail(100)
    last_100_scaled = scaler.transform(last_100).reshape(1, -1, 1)

    future_predictions = []
    for _ in range(no_of_days):
        next_day = model.predict(last_100_scaled, verbose=0)
        future_predictions.append(float(scaler.inverse_transform(next_day)[0][0]))
        last_100_scaled = np.append(last_100_scaled[:, 1:, :], next_day.reshape(1, 1, 1), axis=1)

    color_trend = "#3fb950" if future_predictions[-1] >= future_predictions[0] else "#f85149"

    fig3, ax3 = plt.subplots(figsize=(14, 5))
    days = list(range(1, no_of_days + 1))
    ax3.plot(days, future_predictions, marker="o", markersize=5,
             color=color_trend, linewidth=2, label="Predicted Price")
    ax3.fill_between(days, future_predictions, alpha=0.12, color=color_trend)
    ax3.set_title(f"{stock}  ·  {no_of_days}-Day Price Forecast", fontsize=13, pad=12)
    ax3.set_xlabel("Days Ahead"); ax3.set_ylabel("Predicted Price (20b9 INR)")
    ax3.grid(alpha=0.25, linestyle="--")
    ax3.legend()
    fig3.tight_layout()
    future_plot = plot_to_html(fig3)

    # ── Stats (convert USD → INR) ────────────────────────────────────────────
    inr_rate      = get_usd_to_inr()
    current_price = float(stock_data["Close"].iloc[-1])
    pred_last     = future_predictions[-1]
    pred_change   = ((pred_last - current_price) / current_price) * 100

    current_price_inr = to_inr(current_price, inr_rate)
    pred_last_inr     = to_inr(pred_last, inr_rate)
    future_pred_inr   = [to_inr(p, inr_rate) for p in future_predictions]

    return render_template(
        "result.html",
        stock=stock,
        original_plot=original_plot,
        predicted_plot=predicted_plot,
        future_plot=future_plot,
        future_predictions=future_pred_inr,
        no_of_days=no_of_days,
        current_price=current_price_inr,
        pred_last=pred_last_inr,
        pred_change=round(pred_change, 2),
        inr_rate=round(inr_rate, 2),
        popular_cryptos=POPULAR_CRYPTOS,
    )


@app.route("/compare")
def compare_page():
    return render_template("compare.html", popular_cryptos=POPULAR_CRYPTOS)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
