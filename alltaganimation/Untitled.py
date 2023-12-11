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
class Tagdata:
    def __init__(self,tagname,tagdata):
        self.tagname = tagname
        self.tagdata = tagdata
        


# %%
tagdata = pd.read_csv('testdatafor2312.csv', encoding= 'shift-jis', dtype= 'object', usecols=range(0,5))

# %%
tagdata

# %%
taglist = tagdata['tag'].unique()

# %%
tagdatalist = []
for tag in taglist:
    tag_to_append = Tagdata(tag, tagdata[tagdata['tag'] == tag])
    tagdatalist.append(tag_to_append)

# %%
thistag = tagdatalist[0].tagdata
pilist = tagdata['pino'].unique()
current_data = thistag.iloc[0:15]
df_working = thistag.iloc[0:0]
nm_min = current_data['Number'].min()
#current_data[current_data['Number'] == nm_min]
pd.concat([df_working ,current_data[current_data['Number'] == nm_min]])

# %%
