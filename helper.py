import hashlib as hl
import math
from scipy.stats import norm

# Black-Scholes Call Option Calculation 
def black_scholes_call(spot, strike, time, rf, vol):
  # Calculate d1
  d1 = (math.log(spot/strike) + (rf + 0.5 * vol**2) * time) / (vol * math.sqrt(time))

  # Calculate d2
  d2 = d1 - vol * math.sqrt(time)

  # Calculate call option
  c = spot * norm.cdf(d1) - strike * math.exp(-rf * time) * norm.cdf(d2)

  return float(c)

# Black-Scholes Put Option Calculation
def black_scholes_put(spot, strike, time, rf, vol):
  # Calculate d1
  d1 = (math.log(spot/strike) + (rf + 0.5 * vol**2) * time) / (vol * math.sqrt(time))

  # Calculate d2
  d2 = d1 - vol * math.sqrt(time)

  # Calculate put option
  p = strike * math.exp(-rf * time) * norm.cdf(-d2) - spot * norm.cdf(-d1)

  return float(p)

# Create a range based on a set minimum and maximum value
def create_range(minimum, maximum, n, decimals=0):
  data_range = []
  steps = (maximum - minimum) / (n - 1)

  for i in range(n):
    data_range.append(round((minimum + steps * i), decimals))

  return data_range

# Hashing function for input
def hash_input(stockp, strikep, interestr, vol, time):
  input_str = f"{round(stockp, 6)}-{round(strikep, 6)}-{round(interestr, 6)}-{round(vol, 6)}-{round(time, 6)}"
  return hl.sha256(input_str.encode()).hexdigest()

# Hashing function for output
def hash_output(vol_shock, stockp_shock, optionp, iscall, calc_id):
  input_str = f"{round(vol_shock, 6)}-{round(stockp_shock, 6)}-{round(optionp, 6)}-{int(iscall)}-{calc_id}"
  return hl.sha256(input_str.encode()).hexdigest()