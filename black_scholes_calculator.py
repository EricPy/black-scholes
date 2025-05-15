from db import Session, save_input, save_output, save_single_output, show_recent
from helper import black_scholes_call, black_scholes_put, create_range, hash_input
import math
import matplotlib.pyplot as plt
import pandas as pd
from scipy.stats import norm
import seaborn as sns
import streamlit as st

# App title
st.set_page_config("Black-Scholes Pricing Model")
st.title("Black-Scholes Pricing 📊")

# Simple Black-Scholes Options Calculator
with st.container(border=True):
    st.write("### Option Value Calculator")

    col1_bottom, col2_bottom = st.columns(2)

    spot = col1_bottom.number_input("Spot Price", min_value=0.01, value=40.0) # underlying price
    strike = col2_bottom.number_input("Strike Price", min_value=0.01, value=40.0) # strike price

    col1, col2, col3 = st.columns(3) # Split input into 3 columns

    time = col1.number_input("Time to Maturity (years)", min_value=0.083, value=1.5) # time to expiration
    rf = col2.number_input("Risk-free rate (in %)", min_value=0.01, value=6.0) # risk-free rate
    rf = rf / 100
    vol = col3.number_input("Volatility (σ)", min_value=0.0, value=0.5) # volatility (σ)

    call_option = black_scholes_call(spot, strike, time, rf, vol)
    put_option = black_scholes_put(spot, strike, time, rf, vol)

    # Calculation Result Display
    col_value_1, col_value_2 = st.columns(2)

    font_size = "24px"
    call_value_style = f"color: #FFFFFF; font-size: {font_size}; margin-bottom: 0px; font-weight: 600;"
    put_value_style = f"font-size: {font_size}; margin-bottom: 0px; font-weight: 600;"

    with col_value_1:
      with st.container():
        st.markdown(
          f"""
          <div style='
              background-color: #45ad5b;
              padding: 20px;
              border-radius: 20px;
              text-align: center;
              margin: 20px 10px 30px 5px;
          '> 
              <p style='{call_value_style}'>Call Option Value:</p>
              <p style='{call_value_style}'>{call_option:.2f}</p>
          </div>
          """, 
          unsafe_allow_html=True
        )

    with col_value_2:
      with st.container():
        st.markdown(
          f"""
          <div style='
              background-color: #f8874f;
              padding: 20px;
              border-radius: 20px;
              text-align: center;
              margin: 20px 5px 30px 10px;
          '>
              <p style='{put_value_style}'>Put Option Value:</p>
              <p style='{put_value_style}'>{put_option:.2f}</p>
          </div>
          """,
          unsafe_allow_html=True
        )

# Create Pricing Heatmap
with st.container(border=True):
    # Create range for rows and columns
    st.write("### Option Price Shock Test")

    min_vol = vol - 0.1
    max_vol = vol + 0.1
    min_spot = spot - 9
    max_spot = spot + 9

    col1_range, col2_range = st.columns(2)

    min_vol = col1_range.slider("Minimum Volatility", 0.01, vol, min_vol)
    min_spot = col1_range.number_input("Minimum Spot Price", 0.01, spot, value=min_spot)

    max_vol = col2_range.slider("Maximum Volatility", vol, 2.0, max_vol)
    max_spot = col2_range.number_input("Maxmimum Spot Price", spot, value=max_spot)

    range_vol = create_range(min_vol, max_vol, 10, 2)
    range_spot = create_range(min_spot, max_spot, 10, 2)


    # Create Heatmap Dataframe for Call options
    heatmap_data_call = []

    for volat in range_vol:
      data_row = []

      # Calculate the call option prices
      for s in range_spot:
        # Calculate Call Option Price
        call = black_scholes_call(s, strike, time, rf, volat)

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
        put = black_scholes_put(s, strike, time, rf, volat)

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
with st.container(border=True):
    st.write("### Simulated Profit & Loss")
    
    col1_pur, col2_pur = st.columns(2)
    purchase_call = col1_pur.number_input("Call Purchase Price", min_value=0.01, value=10.0) # Option purchase price
    purchase_put = col2_pur.number_input("Put Purchase Price", min_value=0.01, value=10.0) # Option purchase price

    heatmap_dataframe_call_pnl = heatmap_dataframe_call - purchase_call
    heatmap_dataframe_put_pnl = heatmap_dataframe_put - purchase_put
    heatmap_pnl_col1, heatmap_pnl_col2 = st.columns(2)

    # Plot Call Option Heatmap
    fig3, ax3 = plt.subplots()

    vmax_call = heatmap_dataframe_call.max().max()
    vmin_call = heatmap_dataframe_call.min().min()
    max_abs_call = max(abs(vmax_call), abs(vmin_call))
    
    sns.heatmap(
      heatmap_dataframe_call_pnl, 
      cmap="RdYlGn", 
      center=0, 
      vmin=-max_abs_call,
      vmax=max_abs_call,
      annot=True, 
      fmt=".2f", 
      annot_kws={"size": 8}, 
      ax=ax3
    )

    plt.xlabel("Spot Price", fontsize=8)
    plt.ylabel("Volatility", fontsize=8)
    plt.title("Call Option PnL", fontsize=12)

    heatmap_pnl_col1.pyplot(fig3)

    # Plot Put Option Heatmap
    fig4, ax4 = plt.subplots()

    vmax_put = heatmap_dataframe_put.max().max()
    vmin_put = heatmap_dataframe_put.min().min()
    max_abs_put = max(abs(vmax_put), abs(vmin_put))
    
    sns.heatmap(
      heatmap_dataframe_put_pnl, 
      cmap="RdYlGn", 
      center=0, 
      vmin=-max_abs_put,
      vmax=max_abs_put,
      annot=True, 
      fmt=".2f", 
      annot_kws={"size": 8}, 
      ax=ax4
    )

    plt.xlabel("Spot Price", fontsize=8)
    plt.ylabel("Volatility", fontsize=8)
    plt.title("Put Option PnL", fontsize=12)

    heatmap_pnl_col2.pyplot(fig4)

# Create inputs dataframe
input_data = {
   "stockp": spot,
   "strikep": strike,
   "interestr": rf,
   "vol": vol,
   "time": time
}

input_dataframe = pd.DataFrame([input_data])
input_hash = hash_input(**input_data)

# Create button to save data for later query
if st.button("Store Calculation"):
  session = Session()
  
  try:
    # Save input
    input_id = save_input(input_hash, session, input_dataframe)

    # Save base black-scholes output
    save_single_output(session, vol, spot, call_option, True, input_id, vol, spot)
    save_single_output(session, vol, spot, put_option, True, input_id, vol, spot)

    # Save heatmap output
    save_output(session=session, output_df=heatmap_dataframe_call, iscall=True, base_vol=input_data["vol"], base_stockp=input_data["stockp"], input_id=input_id)
    save_output(session=session, output_df=heatmap_dataframe_put, iscall=False, base_vol=input_data["vol"], base_stockp=input_data["stockp"], input_id=input_id)

    # Commit Changes
    session.commit()
    st.success("Data saved successfully!")

  except Exception as e:
    # Rollback changes in case of failure
    session.rollback()
    print("Rolled back due to:", e)
    st.warning("Failed to save data")

  finally:
    session.close()

    # Show most recent entries into the database
    st.write("#### Most Recently Stored Call / Put Calculations")
    st.dataframe(show_recent(session, 100))


