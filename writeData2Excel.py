import pandas as pd
import os
import sys
from datetime import datetime

########################################################
# Function to get path to resource (works for PyInstaller)
def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def createExcel(saveLoc, data):
    saveNow = datetime.now()
    saveTime = saveNow.strftime("%Y-%m-%d %H-%M-%S")

    # Create excel name (to desktop)
    excelName = 'Scrapped Emails ' + saveTime + '.xlsx'
    outputFileName = os.path.join(saveLoc, excelName)

    # Create excel
    dataframe = pd.DataFrame(data)
    dataframe.columns = ['Email','Town','State','Agency Type','URL']
    writer = pd.ExcelWriter(outputFileName, engine='xlsxwriter')
    dataframe.to_excel(writer, index=False, sheet_name='Sheet1')

    # Format excel document
    workbook = writer.book
    worksheet = writer.sheets['Sheet1']
    for i, col in enumerate(dataframe.columns):
        width = max(dataframe[col].apply(lambda x: len(str(x))).max(), len(col))
        worksheet.set_column(i, i, width)
    writer.close()

    return outputFileName
