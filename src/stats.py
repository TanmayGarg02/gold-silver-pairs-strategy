import numpy as np
import pandas as pd
from typing import Dict

import statsmodels.api as sm
from statsmodels.tsa.stattools import adfuller, coint
from statsmodels.regression.linear_model import OLS
