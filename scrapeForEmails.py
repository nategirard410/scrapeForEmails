# Import modules
import wx
import pandas
import tkinter as tk
from tkinter import messagebox
from tqdm import tqdm
from datetime import datetime
import os
import threading

# Import custom functions
import searchForEmails
import writeData2Excel

########################################################
# Create log file
global logFile
logFile = []

# Create directory if it doesn't exist
folder = "Logs"
if not os.path.isdir(folder):
    os.mkdir(folder)

# Append to log file
global logFileName
global formattedTime
now = datetime.now()
formattedTime = now.strftime("%Y-%m-%d %H-%M-%S")
logFileName = os.path.join(folder, "logFile " + formattedTime + ".log")
with open(logFileName, "a") as file:
    logFile.append('###########################################################################')
    logFile.append('Program executed on ' + formattedTime)


# Calculate the x and y coordinates for a grid layout.
# Implement an offset feature for precise placing.
def getGridLayout(row,column,addSpacex,addSpacey):
    border = 20 # pixels
    spacing = 10 # pixels
    columnWidth = 40 # pixels
    rowHeight = 10 # pixels

    x = border + column*(spacing + columnWidth) + addSpacex
    y = border + row*(spacing + rowHeight) + addSpacey

    return x,y


# If any of the user inputs are not valid, display a message box stating which preset wasn't valid
def throwError(searchError):
    root = tk.Tk()
    root.withdraw()
    title = "Search Parameter Error"

    match searchError:
        case 1:
            message = "No state was choosen. Select a state to continue." # No state chosen
        case 2:
            message = "No cities or towns were choosen. Select cities and towns to continue." # No municipalities chosen
        case 4:
            message = "Custom search prompt was selected but not supplied. Type a custom search prompt to continue." # No search prompt given
        case 7:
            message = "An invalid data type was given for number of websites. Enter a whole number to continue." # Number of searches not an integer 
        case _:
            message = "An unknown error occured. Check the search parameters." # All other, unsupported errors

    messagebox.showinfo(title, message)


def mainProcessing(cities,state,agencyType,numberOfSearches):
    townsNotFound = []
    tableData = []

    print('')
    print('To cancel search, close command window...')

    # Create Header for log file
    logFile.append('Search criteria:')
    logFile.append('     State: ' + state)
    logFile.append('     Search Prompt: ' + agencyType)
    logFile.append('     Number of Searches: ' + str(numberOfSearches))
    logFile.append('     Cities: ')
    for item in cities:
        logFile.append('          ' + item)

    
    for town in tqdm(cities):
        print('')
        try:
            websites = searchForEmails.getWebsites(town,state,agencyType,numberOfSearches)

            if websites:

                # Add data to log file
                logFile.append('')
                logFile.append("Processing " + town + ", " + state)
                logFile.append("     " + str(len(websites)) + " websites were found!")

                # Update user on progress
                print('')
                print("Processing " + town + ", " + state)

                # Scrape for emails
                townEmails, emailURL = searchForEmails.getEmails(websites)
                logFile.append("     " + str(len(townEmails)) + " emails were found!")

                # If no emails were found, add it to a list of towns without emails
                if len(townEmails) == 0:
                    townsNotFound.append(town)

                for emailIndex, email in enumerate(townEmails):
                    tableData.append([email, town, state, agencyType,emailURL[emailIndex]])

        except:
            logFile.append("Error processing " + town + ", " + state,"")
            townsNotFound.append(town)
    

    # Add towns with no emails to the list
    for townIdx in townsNotFound:
        tableData.append(["", townIdx, state,agencyType,""])

    # Export data to excel and format excel
    if tableData:
        outputFileName = writeData2Excel.createExcel(tableData,formattedTime)
        print('')
        print('File saved to: ' + outputFileName)
        logFile.append('')
        logFile.append('File saved to: ' + outputFileName)
        logFile.append('Processing complete.')
    else:
        print("No data to save.")
        messagebox.showinfo('Search Error!', 'No Websites found!')
        return

    # Complete log file and export it. 
    printLogFile(logFile)
    print('')
    print("Processing complete. Waiting for next search...")


def printLogFile(logFile):
    # Append to log file
    with open(logFileName, "a") as file:
        for item in logFile:
            file.write(item + "\n")


class createGUI(wx.Frame):
    # Get the cities that correspond to the state. If no state is choosen,
    # display an empty list
    def getCities(self, event):
        self.state = self.comb.GetStringSelection()
        cities = []

        if self.state == '':
            self.listBox.Set(cities)
        elif self.tableData is not None:
            columnData = list(self.tableData[self.state])
            for item in columnData:
                if type(item) == str:
                    cities.append(item)
            self.listBox.Set(cities) 

    # Check all the items in the listbox or uncheck them all based on
    # which button is pressed. If no state is choosen, return control
    # to the main loop
    def checkList(self, event, action):
        if self.state == '':
            return

        if action == 'check':
            self.listBox.SetCheckedItems(range(self.listBox.GetCount()))
        elif action == 'uncheck':
            items = self.listBox.GetCheckedItems()
            for item in items:
                self.listBox.Check(item, False)

    # Set the interactivity of the text control based on whether its
    # corresponding radion button is picked
    def toggleDialog(self, event):
        if self.radioButton3.Value == True:
            self.dialog.Enable()
        elif self.radioButton3.Value == False:
            self.dialog.SetValue('Enter custom search parameters...')
            self.dialog.Disable()

    def startSearching(self, event):
        # Start the processing in a separate thread to keep GUI responsive
        threading.Thread(target=self._threadedSearch, daemon=True).start()

    def _threadedSearch(self):
        state = self.comb.StringSelection # state
        cities = self.listBox.CheckedStrings # cities
        radio1 = self.radioButton1.Value # search prompt 1
        radio2 = self.radioButton2.Value # search prompt 2
        customSearchPrompt = self.dialog.Value # custom search text
        numberOfSearches = self.searches.Value # number of searches

        # Verify user inputs are valid
        searchError = 0
    
        # Verify state and cities are selected
        if state == '':
            searchError = 1
        elif cities == ():
            searchError = 2

        # Verify user entered a prompt if a custom prompt is used
        customSearch = False
        if radio1 == True:
            agencyType = self.radioButton1.LabelText
        elif radio2 == True:
            agencyType = self.radioButton2.LabelText
        else:
            customSearch = True
            agencyType = customSearchPrompt

        if (customSearchPrompt != '') & (customSearchPrompt != 'Enter custom search parameters...'):
            customSearchPrompt = True

        if (customSearch == True) & (customSearchPrompt != True):
            searchError = 4
            
        # Verify user entered an integer for number of searches
        try:
            numberOfSearches = int(numberOfSearches)
        except:
            searchError = 7

        # If there's an error, notify user
        if searchError != 0:
            wx.CallAfter(throwError, searchError)
            return
        else:
            mainProcessing(cities,state,agencyType,numberOfSearches)

    # Main Gui layout
    def __init__(self):
        # Create application object and frame
        windowWidth = 565
        windowHeight = 600
        wx.Frame.__init__(self, None, -1, "Scrape for Emails 1.0", 
            size = (windowWidth, windowHeight), 
            style=wx.DEFAULT_FRAME_STYLE ^ wx.RESIZE_BORDER)
        pa = wx.Panel(self,-1)
        pa.SetBackgroundColour((214, 216, 217))

        # Initialize empty data structures
        self.tableData = None
        self.statesWithData = ['']
        self.state = ''

        # Create widgets
        statesLabelx,statesLabely = getGridLayout(2,0,60,0)
        self.statesLabel = wx.StaticText(pa, label="Search Locations", pos=(statesLabelx, statesLabely))

        listBoxx,listBoxy = getGridLayout(6,0,0,0)
        listboxHeight = windowHeight - (listBoxy + 60)
        self.listBox = wx.CheckListBox(pa, -1, choices=["Loading..."], pos = (listBoxx, listBoxy), size = (-1,listboxHeight))
        listBoxSize = self.listBox.Size
        listBoxSize.SetWidth(210)
        self.listBox.Size = listBoxSize

        combx,comby = getGridLayout(3,0,0,0)
        self.comb = wx.Choice(pa, choices = self.statesWithData, pos = (combx,comby))
        combSize = self.comb.Size
        combSize.SetWidth(210)
        self.comb.Size = combSize
        self.comb.Bind(wx.EVT_CHOICE, self.getCities)

        checkButtonx,checkButtony = getGridLayout(4,0,0,10)
        self.checkButton = wx.Button(pa, -1, "Check All", pos = (checkButtonx, checkButtony))
        self.checkButton.Bind(wx.EVT_BUTTON, lambda event: self.checkList(event, 'check'))

        uncheckButtonx,uncheckButtony = getGridLayout(4,2,27,10)
        self.uncheckButton = wx.Button(pa, -1, "Uncheck All", pos = (uncheckButtonx, uncheckButtony))
        self.uncheckButton.Bind(wx.EVT_BUTTON, lambda event: self.checkList(event, 'uncheck'))

        searchLabelx,searchLabely = getGridLayout(2,5,75,0)
        self.searchLabel = wx.StaticText(pa, label="Search Parameters", pos=(searchLabelx, searchLabely))

        dialogx,dialogy = getGridLayout(5,5,0,0)
        self.dialog = wx.TextCtrl(pa, -1, pos = (dialogx, dialogy))
        dialogSize = self.dialog.Size
        dialogSize.SetWidth(256)
        self.dialog.Size = dialogSize
        self.dialog.Value = 'Enter custom search parameters...'
        self.dialog.Disable()

        radioButton3x,radioButton3y = getGridLayout(4,5,0,0)
        self.radioButton3 = wx.RadioButton(pa, -1, "Custom Search", pos = (radioButton3x, radioButton3y))
        self.radioButton3.Bind(wx.EVT_RADIOBUTTON, self.toggleDialog)

        radioButton1x,radioButton1y = getGridLayout(3,5,0,0)
        self.radioButton1 = wx.RadioButton(pa, -1, "EMS Agency", pos = (radioButton1x, radioButton1y))
        self.radioButton1.SetValue(True)
        self.radioButton1.Bind(wx.EVT_RADIOBUTTON, self.toggleDialog)

        radioButton2x,radioButton2y = getGridLayout(3,7,35,0)
        self.radioButton2 = wx.RadioButton(pa, -1, "Ambulance Service", pos = (radioButton2x, radioButton2y))
        self.radioButton2.Bind(wx.EVT_RADIOBUTTON, self.toggleDialog)

        numberLabelx,numberLabely = getGridLayout(6,6,35,15)
        self.numberLabel = wx.StaticText(pa, label="Number of Websites:", pos=(numberLabelx, numberLabely))

        searchesx,searchesy = getGridLayout(6,8,56,10)
        self.searches = wx.TextCtrl(pa, -1, pos = (searchesx, searchesy), style=wx.TE_RIGHT)
        searchesSize = self.searches.Size
        searchesSize.SetWidth(50)
        self.searches.Size = searchesSize
        self.searches.Value = '10'

        runButtonx,runButtony = getGridLayout(8,8,16,0)
        self.runButton = wx.Button(pa, -1, "Run Program", pos = (runButtonx, runButtony))
        self.runButton.Bind(wx.EVT_BUTTON, self.startSearching)

        # Start a thread to load Excel data in the background
        threading.Thread(target=self.loadExcelData, daemon=True).start()

    # Load Excel data asynchronously
    def loadExcelData(self):
        try:
            self.tableData = pandas.read_excel('US_States_Cities.xlsx', sheet_name='Sheet1')
            allStates = self.tableData.columns
            for it, stateName in enumerate(allStates):
                if type(self.tableData.iloc[0,it]) == str:
                    self.statesWithData.append(stateName)

            # Update the combo box on the main thread
            wx.CallAfter(self.comb.Set, self.statesWithData)

            # Clear the placeholder in the listbox
            wx.CallAfter(self.listBox.Set, [])
        except Exception as e:
            print("Error loading US_States_Cities.xlsx:", e)


# Show it and start the event loop
if __name__ == "__main__":
    app1 = wx.App()
    frame = createGUI()
    frame.Show()
    app1.MainLoop()
