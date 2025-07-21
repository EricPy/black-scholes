# 📈 Black-Scholes Option Pricing App

#### Video Demo: https://youtu.be/_wbJ1iuBZ9Q
#### Description:

This project is an interactive web application that calculates and visualizes option prices using the Black-Scholes model. It’s built using Python, Streamlit for the front end, and SQLAlchemy with SQLite for local data storage. The app supports inputting option parameters, visualizing profit and loss heatmaps, and storing previous calculations for querying and reuse.

The app started as a pet project I wanted to do to get into the realm of quant finance. It was made based on the descriptions (only, no code were copied from external sources) given by this video:
https://www.youtube.com/watch?v=lY-NP4X455U

The video itself was made as a commentary on a project someone else made, and what features could be added to it. Here's the other person's project:
https://blackschole.streamlit.app/

I wanted to understand how Black-Scholes works first, so initially I practiced making the calculations in a google colab notebook:
https://colab.research.google.com/drive/1Qgiumx2mZttQ-Oia1urWORhuOF7gkjcf?usp=sharing

Once I got that down it was time to implement it in an actual user interactive web app. While it's still quite simple, I’m proud that it integrates multiple technologies in a cohesive way.

---

## 🧠 What the App Does

The core functionality of the app is to help users (or myself) understand how option prices — both call and put — change based on parameters like spot price, strike price, volatility, time to maturity, and the risk-free rate. After entering values, the app calculates both the call and put price using the Black-Scholes model and displays them clearly. It also allows the user to simulate profit and loss scenarios by creating heatmaps of option values over a range of volatilities and spot prices.

The PnL heatmaps are color-coded using a diverging color scheme: red for negative values, white for break-even (0), and green for profit. I used Seaborn’s `RdYlGn` palette and set it up so that the color scale dynamically centers around zero and still works well even when all values are positive or negative.

Beyond just viewing results, the app stores inputs and outputs in a local SQLite database using SQLAlchemy ORM. To avoid redundant records, I implemented a hashing function for both input and output records. Each unique combination of parameters creates a SHA-256 hash, which is used as a unique identifier to avoid inserting duplicate rows.

The database implementation definitely took the longest as I was completely new to the SQLAlchemy library before starting this project.

---

## 📁 File Breakdown

### `black_scholes_calculator.py`
This is the main Streamlit application file. It contains the layout and user interface for entering parameters, displaying results, generating heatmaps, and triggering database saves. It also contains logic for gathering user inputs, calling pricing functions, and storing results. The app is organized into sections (inputs, results, heatmaps, and database storage), and Streamlit containers/columns are used to keep the layout clean and responsive.

### `helper.py`
This file contains the core mathematical functions used in the app. It implements the Black-Scholes formulas for call and put options using the standard `math` and `scipy.stats.norm` libraries. It also includes utility functions like `create_range()` for generating heatmap axes and `hash_input()` / `hash_output()` for SHA-256-based deduplication of stored records.

### `db.py`
This is the backend file responsible for database modeling and interactions. It defines two SQLAlchemy ORM models: `BsInput` and `BsOutput`. These represent the input parameters and the corresponding output data (option prices, shocks, etc.). The two models are connected via a foreign key relationship (`calc_id`). The file also includes functions to save inputs and outputs to the database, check for existing records via hash comparisons, and fetch the most recent records for display in the app.

---

## 🔍 Design Decisions

### Storing Data with Hashes
One early question I faced was: how can I avoid saving the same calculation multiple times? My first thought was to compare all input fields before insertion, but that felt repetitive and hard to scale. Instead, I created a `hash_input()` function that hashes all inputs into a single SHA-256 string, and used that as a unique constraint. The same is done for outputs. This made deduplication simple and efficient.

### Heatmap Coloring
Another small challenge was choosing the right color scale. At first, `center=0` alone wasn’t enough — when all values were positive, the heatmap would look flat and lose contrast. To solve this, I added `vmin` and `vmax` parameters dynamically, using the max absolute value of the data range to force symmetric scaling. This ensured that heatmaps always had visual contrast, even in edge cases.

### Data Model
The data model is intentionally normalized — inputs are stored in one table, and outputs in another. Each output references an input by foreign key. I debated combining them into one table for simplicity, but separating them allows for flexibility if I ever want to generate multiple outputs from a single input (e.g., for different models).

---

## 🚀 Running the App

To run the app locally:

1. Clone the repo
2. Install dependencies: `pip install -r requirements.txt`
3. Run the app: `streamlit run black_scholes_calculator.py`

This was Black Scholes Options Pricer
