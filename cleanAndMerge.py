import os
import pandas as pd

# read the csv file into a pandas dataframe
df = pd.read_csv('inptt/OTR.Biases_OTR.BIASES_otr_1_1.csv')

# remove duplicates based on all columns
df.drop_duplicates(inplace=True)
#drop the last row
df.drop(df.tail(1).index, inplace=True)

# write the cleaned dataframe back to a csv file
df.to_csv('filename_cleaned.csv', index=False)
