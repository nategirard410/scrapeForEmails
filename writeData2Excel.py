import pandas as pd
import os


def createExcel(data,formattedTime):
    # Create excel name (to desktop)
    excelName = 'Scrapped Emails ' + formattedTime + '.xlsx'
    desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
    outputFileName = os.path.join(desktop_path, excelName)

    # Create excel
    dataframe = pd.DataFrame(data)
    dataframe.columns = ['Email','Town','State','Agency Type']
    writer = pd.ExcelWriter(outputFileName, engine='xlsxwriter')
    dataframe.to_excel(writer, index=False, sheet_name='Sheet1')

    # Format excel document
    workbook = writer.book
    worksheet = writer.sheets['Sheet1']
    for i, col in enumerate(dataframe.columns):
        width = max(dataframe[col].apply(lambda x: len(str(x))).max(), len(col))
        worksheet.set_column(i, i, width)
    writer._save()

    return outputFileName