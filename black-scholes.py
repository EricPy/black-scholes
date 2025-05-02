from helper import black_scholes_call, black_scholes_put, create_range
import math
import matplotlib.pyplot as plt
import pandas as pd
from scipy.stats import norm
import seaborn as sns
import streamlit as st


st.title("Black-Scholes Options Price Simulation")

# Request user input
st.write("### Input Data")

col1, col2, col3 = st.columns(3) # Split input into 3 columns

spot = col1.number_input("Spot Price", min_value=0.01, value=100) # underlying price
strike = col1.number_input("Strike Price", min_value=0.01, value=100 ) # strike price

time = col2.number_input("Time to Maturity", min_value=0.083, value=1) # time to expiration
rf = (col2.number_input("Risk-free rate (in %)", min_value=0.01, value=5)) / 100 # risk-free rate

vol = col3.number_input("Volatility (σ)", min_value=0.0, value=0.2) # volatility (σ)

# Generate heatmap based on input
sns.set_context("notebook", font_scale=0.8)