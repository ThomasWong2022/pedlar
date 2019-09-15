import os
import datetime
import csv
import time

import requests

import pandas as pd
import numpy as np

iexbaseurl = 'https://api.iextrading.com/1.0'

def get_TOPS(tickerstring):
    

