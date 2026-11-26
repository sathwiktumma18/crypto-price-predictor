# 🔮 CryptoScope — Cryptocurrency Price Predictor

A web application that uses an **LSTM deep learning model** to predict future cryptocurrency closing prices. Built with **Flask**, **TensorFlow/Keras**, and **yfinance**, featuring a sleek dark-themed UI with live ticker prices in INR.

---

## 📋 Table of Contents

1. [Prerequisites](#-prerequisites)
2. [Download & Open the Project](#-download--open-the-project)
3. [Set Up a Virtual Environment (Recommended)](#-set-up-a-virtual-environment-recommended)
4. [Install Dependencies](#-install-dependencies)
5. [Run the Application](#-run-the-application)
6. [Using the Application](#-using-the-application)
7. [Project Structure](#-project-structure)
8. [Troubleshooting](#-troubleshooting)

---

## 🛠 Prerequisites

Before you begin, make sure the following are installed on your computer:

### 1. Python (version 3.9 or above)

1. Go to [https://www.python.org/downloads/](https://www.python.org/downloads/)
2. Download the latest Python installer for your OS.
3. **Important (Windows):** During installation, **check the box** that says **"Add Python to PATH"**.
4. To verify, open a terminal and run:
   ```
   python --version
   ```
   You should see something like `Python 3.11.x`.

### 2. Visual Studio Code (VS Code)

1. Go to [https://code.visualstudio.com/](https://code.visualstudio.com/)
2. Download and install VS Code for your operating system.
3. **(Optional but recommended):** Install the **Python extension** in VS Code:
   - Open VS Code → Click the **Extensions** icon on the left sidebar (or press `Ctrl+Shift+X`).
   - Search for **"Python"** by Microsoft → Click **Install**.

### 3. Git (Optional — only needed if cloning from GitHub)

- Download from [https://git-scm.com/downloads](https://git-scm.com/downloads)

---

## 📂 Download & Open the Project

### Option A: Download as ZIP

1. On the GitHub repository page, click the green **"Code"** button → **"Download ZIP"**.
2. Extract the ZIP file to a folder on your computer (e.g., `C:\Users\YourName\Downloads\cryptocurrency_price_predictor-main`).

### Option B: Clone with Git

Open a terminal and run:

```bash
git clone https://github.com/YOUR_USERNAME/cryptocurrency_price_predictor.git
```

### Open in VS Code

1. Open **VS Code**.
2. Go to **File → Open Folder**.
3. Navigate to the project folder (the one containing `app.py`) and click **Select Folder**.
4. You should now see all the project files in the **Explorer** panel on the left.

---

## 🐍 Set Up a Virtual Environment (Recommended)

A virtual environment keeps the project's dependencies isolated from your system Python. This avoids conflicts with other projects.

### Open the Terminal in VS Code

- Press `` Ctrl + ` `` (backtick) to open the integrated terminal, **OR**
- Go to **Terminal → New Terminal** from the menu bar.

### Create the Virtual Environment

Run this command in the terminal:

```bash
python -m venv venv
```

This creates a folder called `venv` inside your project directory.

### Activate the Virtual Environment

**Windows (Command Prompt):**

```bash
venv\Scripts\activate
```

**Windows (PowerShell):**

```bash
.\venv\Scripts\Activate.ps1
```

> **⚠️ PowerShell Error?** If you get a "running scripts is disabled" error, run this command first:
>
> ```bash
> Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
> ```
>
> Then try activating again.

**macOS / Linux:**

```bash
source venv/bin/activate
```

✅ **You'll know it worked** when you see `(venv)` at the beginning of your terminal prompt.

---

## 📦 Install Dependencies

With the virtual environment **activated**, install all required packages by running:

```bash
pip install -r requirements.txt
```

This installs the following libraries:

| Package        | Purpose                                 |
| -------------- | --------------------------------------- |
| `flask`        | Web framework for the app               |
| `pandas`       | Data manipulation                       |
| `numpy`        | Numerical computations                  |
| `yfinance`     | Fetches live crypto/stock data          |
| `keras`        | Deep learning model loading             |
| `tensorflow`   | Backend for Keras (LSTM model)          |
| `scikit-learn`  | Data preprocessing (MinMaxScaler)      |
| `matplotlib`   | Generating price charts                 |

> **⏳ Note:** TensorFlow is a large package (~400–500 MB). The installation may take a few minutes depending on your internet speed.

---

## ▶️ Run the Application

Once all dependencies are installed, start the Flask development server:

```bash
python app.py
```

You should see output similar to:

```
 * Serving Flask app 'app'
 * Debug mode: on
 * Running on http://127.0.0.1:5000
Press CTRL+C to quit
```

### Open the App in Your Browser

1. Hold `Ctrl` and **click** the link `http://127.0.0.1:5000` in the terminal, **OR**
2. Open your web browser manually and go to: **http://127.0.0.1:5000**

🎉 **The app is now running!**

### Stop the Server

Press `Ctrl + C` in the terminal to stop the server.

---

## 🚀 Using the Application

### Home Page — Make a Prediction

1. **Enter a ticker symbol** in the input field (e.g., `BTC-USD` for Bitcoin, `ETH-USD` for Ethereum).
   - You can also click one of the **Quick Select** chips to auto-fill.
2. **Set the forecast horizon** using the slider (1–100 days).
3. Click **🔮 Run Prediction**.
4. Wait a few seconds while the model processes the data.

### Results Page

After processing, you'll see:

- **📊 Stat Cards** — Current price, forecasted price, and expected % change (in INR).
- **📈 Historical Closing Prices** — A chart showing the asset's price over the last 10 years.
- **🔵 Actual vs Predicted** — How well the model performed on test data.
- **🔮 Future Forecast** — Predicted prices for your chosen number of days.
- **📋 Day-by-Day Table** — Detailed breakdown of each predicted day.

### Compare Page

Click **Compare** in the navigation bar to compare performance of multiple cryptocurrencies side by side.

### Live Ticker Bar

The scrolling bar at the top shows **real-time prices** of popular cryptocurrencies in INR, updated every 60 seconds.

---

## 📁 Project Structure

```
cryptocurrency_price_predictor/
│
├── app.py                  # Main Flask application (routes, model logic)
├── model.keras             # Pre-trained LSTM model file
├── requirements.txt        # List of Python dependencies
├── README.md               # This file
│
├── templates/              # HTML templates (Jinja2)
│   ├── base.html           # Base layout (navbar, ticker bar, styles)
│   ├── index.html          # Home page with prediction form
│   ├── result.html         # Results page with charts and table
│   └── compare.html        # Crypto comparison page
│
└── CryptoCurrency(Bitcoin) Price Prediction.ipynb
                            # Jupyter notebook used to train the model
```

---

## ❓ Troubleshooting

### "python is not recognized as a command"

- Python is not added to your system PATH.
- **Fix:** Reinstall Python and make sure to check **"Add Python to PATH"** during installation.
- Alternatively, try using `python3` instead of `python`.

### "pip is not recognized"

- Try: `python -m pip install -r requirements.txt`

### TensorFlow installation fails

- Make sure you're using **Python 3.9–3.12** (TensorFlow may not support the very latest Python).
- Try upgrading pip first: `python -m pip install --upgrade pip`

### "Running scripts is disabled on this system" (PowerShell)

- Run: `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`

### Port 5000 already in use

- Another application is using port 5000.
- **Fix:** Change the port in `app.py` by modifying the last line:
  ```python
  app.run(debug=True, port=5001)
  ```

### App runs but no data is shown

- Make sure you have an **active internet connection** — the app fetches live data from Yahoo Finance.
- Check that the ticker symbol is valid (use [Yahoo Finance](https://finance.yahoo.com/) to verify).

---

## 📝 License

This project is for **educational purposes only**. Predictions are generated by a machine learning model and **do not constitute financial advice**.

---

> **Built with ❤️ using Flask, TensorFlow, and yfinance**