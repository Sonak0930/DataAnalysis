import streamlit as st
import numpy as np
import pandas as pd


folder_path='data/SeoulBike'
filelist =os.listdir(folder_path)

df=[]
for file in filelist:
    if file.endswith(".csv"):
        path=os.path.join('data/SeoulBike/',file)
        df.append(pd.read_csv(path))

bike = pd.concat(df,ignore_index=True)