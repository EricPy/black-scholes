from helper import black_scholes_call, black_scholes_put, create_range
import math
import matplotlib.pyplot as plt
import pandas as pd
from scipy.stats import norm
import seaborn as sns
import streamlit as st

# App title
st.title("Black-Scholes Options Price Simulation")


# Request user input
st.write("### Input Simulaiton Data")

col1, col2, col3 = st.columns(3) # Split input into 3 columns

spot = col1.number_input("Spot Price", min_value=0.01, value=100.0) # underlying price
strike = col1.number_input("Strike Price", min_value=0.01, value=100.0) # strike price

time = col2.number_input("Time to Maturity", min_value=0.083, value=1.0) # time to expiration
rf = (col2.number_input("Risk-free rate (in %)", min_value=0.01, value=5.0)) / 100.0 # risk-free rate

vol = col3.number_input("Volatility (σ)", min_value=0.0, value=0.2) # volatility (σ)
purchase = col3.number_input("Purchase Price", min_value=0.01, value=100.0) # Option purchase price

call_option = black_scholes_call(spot, strike, time, rf, vol)
put_option = black_scholes_put(spot, strike, time, rf, vol)

st.write(f"Call Option: {call_option}")
st.write(f"Put Option: {put_option}")

# Create range for rows and columns
min_vol = vol - 0.1
max_vol = vol + 0.1
min_spot = spot - 10
max_spot = spot + 10

range_vol = create_range(min_vol, max_vol, 10, 2)
range_spot = create_range(min_spot, max_spot, 10)


# Create Heatmap Dataframe for Call options
heatmap_data_call = []

for volat in range_vol:
  data_row = []

  # Calculate the call option prices
  for s in range_spot:
    # Calculate Call Option Price
    call = black_scholes_call(s, strike, rf, time, volat)

    data_row.append(round(call, 2))

  # Append row to the data
  heatmap_data_call.append(data_row)

heatmap_dataframe_call = pd.DataFrame(heatmap_data_call, index=range_vol, columns=range_spot)


# Create Heatmap Dataframe for Call options
heatmap_data_put = []

for volat in range_vol:
  data_row = []

  # Calculate the put option prices
  for s in range_spot:
    # Calculate put Option Price
    put = black_scholes_put(s, strike, rf, time, volat)

    data_row.append(round(put, 2))

  # Append row to the data
  heatmap_data_put.append(data_row)

heatmap_dataframe_put = pd.DataFrame(heatmap_data_put, index=range_vol, columns=range_spot)


# Generate heatmap based on input
sns.set_context("notebook", font_scale=0.8)
heatmap_col1, heatmap_col2 = st.columns(2)

# Plot Call Option Heatmap
fig1, ax1 = plt.subplots()
sns.heatmap(heatmap_dataframe_call, cmap="viridis", annot=True, fmt=".2f", annot_kws={"size": 8}, ax=ax1)

# Add Titles
plt.xlabel("Spot Price", fontsize=8)
plt.ylabel("Volatility", fontsize=8)
plt.title("Call Option Pricing", fontsize=12)

heatmap_col1.pyplot(fig1)

# Plot Put Option Heatmap
fig2, ax2 = plt.subplots()
sns.heatmap(heatmap_dataframe_put, cmap="viridis", annot=True, fmt=".2f", annot_kws={"size": 8}, ax=ax2)

# Add Titles
plt.xlabel("Spot Price", fontsize=8)
plt.ylabel("Volatility", fontsize=8)
plt.title("Put Option Pricing", fontsize=12)

heatmap_col2.pyplot(fig2)

# Create PnL dataframes
heatmap_dataframe_call_pnl = heatmap_dataframe_call - purchase
heatmap_dataframe_put_pnl = heatmap_dataframe_put - purchase
heatmap_pnl_col1, heatmap_pnl_col2 = st.columns(2)

# Plot Call Option Heatmap
fig3, ax3 = plt.subplots()
sns.heatmap(heatmap_dataframe_call_pnl, cmap="RdYlGn", annot=True, fmt=".2f", annot_kws={"size": 8}, ax=ax3)

plt.xlabel("Spot Price", fontsize=8)
plt.ylabel("Volatility", fontsize=8)
plt.title("Call Option PnL", fontsize=12)

heatmap_pnl_col1.pyplot(fig3)

# Plot Put Option Heatmap
fig4, ax4 = plt.subplots()
sns.heatmap(heatmap_dataframe_put_pnl, cmap="RdYlGn", annot=True, fmt=".2f", annot_kws={"size": 8}, ax=ax4)

plt.xlabel("Spot Price", fontsize=8)
plt.ylabel("Volatility", fontsize=8)
plt.title("Put Option PnL", fontsize=12)

heatmap_pnl_col2.pyplot(fig4)