from constants import RESOLUTION
from func_utils import get_ISO_times
import pandas as pd
import numpy as np
import time
from pprint import pprint

# Get relevant time periods for ISO from and to
ISO_time = get_ISO_times()

pprint(ISO_time)  # Changed from ISO_TIMES to ISO_time based on the variable you defined above

# Construct market prices
def construct_market_prices(client):
    pass
