# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.14.4
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# %%
import csv
import os
import sys
from time import time
import numpy as np
from scipy import interpolate
import datetime
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.animation import ArtistAnimation
import random
import math
import pathlib
import operator
from matplotlib.animation import FuncAnimation
from matplotlib import patches
import pykalman
import copy

# %%
tagdata = pd.read_csv('timedatatest.csv', encoding= 'shift-jis', dtype= 'object', usecols=(0,2,4,5,7))
tagdata.columns=['time','tag','Number','LQI','pino']

# %%
tagdata.to_csv('testdatafor2312.csv',encoding = 'shift-jis',index=False)

# %%
