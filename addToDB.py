import os
import sqlite3
import pandas as pd
#from main import df_res

conn = sqlite3.connect('rdmData.db')
c = conn.cursor()



#get the files located in the input folder
files = os.listdir('input')
#loop through the files
for file in files:
    tempData = pd.read_csv('input/'+file, sep=';')
    print(tempData)
    tempData = tempData.replace(';', ',', regex=True)
    tempData = tempData.replace(',', '.', regex=True)
    #change date from dd-mm-yy to dd/mm/yy
    tempData['Date'] = tempData['Date'].str.replace('-', '/')
    #convert to datetime
    #tempData['Date'] = pd.to_datetime(tempData['Date'], format='%d/%m/%Y')
    #remove duplicates based on all columns
    tempData.drop_duplicates(inplace=True)
    print(tempData)

    tempData.to_sql('tblGegevens', conn, if_exists='append', index=False)

    #remove the file from the input folder
    os.remove(os.path.join('input', file))

# commit changes
conn.commit()

