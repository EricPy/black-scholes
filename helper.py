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