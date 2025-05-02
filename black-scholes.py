from helper import black_scholes_call, black_scholes_put, create_range
import math
import matplotlib.pyplot as plt
import pandas as pd
from scipy.stats import norm
import seaborn as sns
import streamlit as st

sns.set_context("notebook", font_scale=0.8)

# Request user input
st.title("Black-Scholes Options Price Simulation")

# Generate heatmap based on input