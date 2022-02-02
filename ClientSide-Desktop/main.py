import PyQt5.QtWidgets as qtw
import PyQt5.QtGui     as qtg
import PyQt5.QtCore    as qtc
import requests        as req
import sys
import tkinter         as tk
from PIL import ImageTk, Image
import requests        as req
from tkinter import messagebox
from PyQt5.QtCore import QTimer, QTime, Qt
import json
import PyQt5.QtWebEngineWidgets as qtWebEngineLOADER
import os
import os.path as osPath
import pyautogui
from widgetPercentageValue import widgetPercentageValue
import time
import win32api
import win32print
import io
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


# Importing the server URL;
from AppData import ServerUrl
# Importing the product data path;
from AppData import ProductDataPath
# TVSH VALUE;
from AppData import TVSHVALUEPERCENTAGE
# COLORS;
from AppData import COLORS

# ----  Importing my own modules  ----;
# PyQt5 percentage value function;
sys.path.append(r"C:\Users\Led-Com.CH\Desktop\AdaksPythonLibrary")
from AdaksPyQt5Tools import PercentageValue as adakPV

# Gradient animation button;
from AdaksPyQt5Tools import AnimatedButton
# Easily resizable checkbox;
from AdaksPyQt5Tools import adakCheckButton

# MainPage footer buttons;
from footerButtons_MP import footerButtons_MP
# Seperator Lines;
from seperatorLineF import seperatorLineF
# is_numeric for checking if a number is a float;
from is_numeric import is_number
# Frame seperator Lines;
from frameSeperatorLineF import frameSeperatorLineF
# Full time actual bill file data sorter function;
from fullTimeActualBillDataSorterF import fullTimeActualBillDataSorterF


# Global Data;
GLOBALUSERDATA = {}
# Request timer single start locker:
requestTimerHasStarted = False



# Main Window;
class MainWindow(qtw.QWidget):
    def __init__(self):
        super().__init__()
        # The laststate holder;
        self.lastRequestState = {}

        # Starting the request timer only if it hasn't started yet;
        global requestTimerHasStarted
        if not(requestTimerHasStarted):
            requestTimerHasStarted = True
            self.startRequestTimerF()

        # Self styling;
        self.setStyleSheet("""
        QPushButton:hover:!pressed
            {
                background-color: #ddd;
            }
        """)

        # State Data;
        self.allTables = []


        # Loading the settings for the mainpage;
        with open("./Data/settings.json") as stl:
            self.SETTINGS = json.load(stl)["mainPageSettings"]
        print(self.SETTINGS)

        # Displaying some basic data on the top;
        # Header frame;
        self.headerFrame = qtw.QFrame(self)
        self.headerFrame.setFixedSize(adakPV(100, "w", app), adakPV(18, "h", app))
        self.headerFrame.setStyleSheet(f"background-color: {self.SETTINGS['headerColor']};")
        self.headerFrame.move(0, 0)

        # TABLES RELATED DATA / FUNCTION CALLS;
        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        
        # Tables location;
        self.tablesScroller = qtw.QScrollArea(self)
        self.tablesScroller.setWidgetResizable(True)
        self.scrollAreaWidgetContents = qtw.QWidget()
        self.tablesScroller.setStyleSheet("background-color: #282636;")
        self.tablesScroller.setFixedSize(adakPV(100, "w", app), adakPV(82, "h", app))
        self.tablesScroller.move(0, adakPV(18, "h", app))
        self.tablesGrid = qtw.QGridLayout(self.scrollAreaWidgetContents)
        self.tablesScroller.setWidget(self.scrollAreaWidgetContents)

        
        # Loading the tables;
        self.renderTablesF()
        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

        # Bottom Navigation Box;
        self.bottomNavigationFrame = qtw.QFrame(self)
        self.bottomNavigationFrame.setFixedSize(adakPV(60, "w", app), adakPV(23, "h", app))
        self.bottomNavigationFrame.setStyleSheet(f"background-color: {self.SETTINGS['footerColor']};border-radius: 50%; border: 2px solid white;")
        self.bottomNavigationFrame.move(adakPV(20, "w", app), adakPV(82, "h", app))
        

        # Bottom Navigation Box Buttons;
        footerButtons_MP(self, 24, 93, lambda: self.goToStatisticsPageF(), app, "Statistics")
        footerButtons_MP(self, 64, 93, lambda: self.goToStandbyF(), app, "Standby")
        footerButtons_MP(self, 24, 85, lambda: self.goToProductsScreen(), app, "Products")
        footerButtons_MP(self, 64, 85, lambda: self.goToSettingsScreen(), app, "Settings")
        footerButtons_MP(self, 44, 93, lambda: self.goToBrowserWidget(), app, "Browser")
        footerButtons_MP(self, 44, 85, lambda: self.goToTakeAwaysScreen(), app, "Take Aways")

        # Take away count frame;
        self.takeAwayCountFrame = qtw.QFrame(self)
        self.takeAwayCountFrame.setStyleSheet("background-color: red; color: white; border: 1px solid purple;")
        self.takeAwayCountFrame.setFixedSize(adakPV(4, "w", app), adakPV(3, "h", app))
        self.takeAwayCountFrame.move(adakPV(43, "w", app), adakPV(84, "h", app)-2)

        # Take away count label;
        self.takeAwayCountLabel = qtw.QLabel("-------", self.takeAwayCountFrame)
        self.takeAwayCountLabel.setFont(qtg.QFont("Arial", int(adakPV(1, "w", app)*1.1)))
        self.takeAwayCountLabel.move(0, 0)


        #========================================================================================================================
    

    # #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # Navigation Functions;
    def goToStatisticsPageF(self):
        appStack.setCurrentIndex(gotoStatisticsINDEX)
    def goToStandbyF(self):
        appStack.setCurrentIndex(goToStandbyINDEX)
    def goToProductsScreen(self):
        appStack.setCurrentIndex(gotoProductsINDEX)
    def goToSettingsScreen(self):
        appStack.setCurrentIndex(gotoSettingsINDEX)
    def goToBrowserWidget(self):
        self.openedBrowser = BrowserWidget()
    def goToTakeAwaysScreen(self):
        self.takeAwayWidget = TakeAwayWidget()
    # #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    

    def renderTablesF(self):
        constantButtonSize = self.SETTINGS["tableButtonConstantMax"]
        maxCols = int(app.primaryScreen().size().width()/constantButtonSize)
        x=0
        y=0
        for i in range(GLOBALUSERDATA["userData"]["tableCount"]): # Looping through it based of the amount of tables the client has;
            if y >= maxCols:
                y=0
                x+=1
            shadow = qtw.QGraphicsDropShadowEffect()
            shadow.setBlurRadius(15)
            shadow.setOffset(adakPV(1, 'w', app)/6)
            shadow.setColor(qtg.QColor("aqua"))
            tableButton = qtw.QPushButton(f"Table {i+1}", clicked=lambda ignore, btnid=i: self.viewDesiredTableByTableButton(btnid))
            tableButton.setFont(qtg.QFont("arial", adakPV(1.1, "w", app)))
            tableButton.setStyleSheet("color: white; border: 1px solid aqua; border-radius: 20px;")
            # Checking which backgroundd color to use;
            # If the index'ed table is filled, the color will be red;
            if GLOBALUSERDATA["userData"]["tableFillStates"][i]:
                shadow.setColor(qtg.QColor("purple"))
                tableButton.setStyleSheet("color: white; border: 1px solid purple; border-radius: 20px; background-color: red;")
            tableButton.setFixedSize(constantButtonSize, 100)
            tableButton.setGraphicsEffect(shadow)

            self.allTables.append(tableButton) # Appending the button to the buttons array;

            self.tablesGrid.addWidget(tableButton, x, y)
            y+=1
        # adding the bottom filler;
        bottomFiller = qtw.QFrame()
        bottomFiller.setStyleSheet("background-color: #282636;")
        bottomFiller.setFixedSize(adakPV(1, "w", app), adakPV(30, "h", app))
        self.tablesGrid.addWidget(bottomFiller, x+1, y+1)


    # Showing the takeAway count on a small alert-box on the take away's screen button;
    def showTakeAwayCountOnTakeAwayButtonF(self):
        takeAwayCount = GLOBALUSERDATA["userData"]["takeAwayCount"]
        print(takeAwayCount)
        if takeAwayCount < 999:
            self.takeAwayCountLabel.setText(str(takeAwayCount))
        else:
            self.takeAwayCountLabel.setText("999+")



    # Destroying all the buttons;
    def destroyAllTableButtonsF(self):
        for button in self.allTables:
            button.setParent(None)


    def sendServerRequestF(self):
        global GLOBALUSERDATA
        # Sending the request to the server for the table data;
        print(f"sendServerRequestF: {GLOBALUSERDATA}")
        # Hitting the login path of my server as that path returns back exactly the data i need to be able to assign it to my GLOBALUSERDATA;
        # Then destroy all the buttons and set them back as they are so they will get the colors automatically;
        tablesRequestResponse = req.post(f"{ServerUrl}login", data={"restaurantID": GLOBALUSERDATA["restaurantID"], "password": GLOBALUSERDATA["password"]}).json()
        # Checking if the laststate is the same as the request state, if it is same, not doing anything, otherwise, rerendering the screen;
        
        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        # The code below makes no sense for lots of reasons yet it works only this way soo....
        #             _  _  _____                                  ___          ___                    
        # _| || |_   / / / |  _  \                                 | |          | |                  _ 
        #|_  __  _| / / /  | | | |_ __ __ _  __ _  ___  _ __  ___  | |__   ___  | |__   ___ _ __ ___(_)
        # _| || |_ / / /   | | | | '__/ _` |/ _` |/ _ \| '_ \/ __| | '_ \ / _ \ | '_ \ / _ \ '__/ _ \  
        #|_  __  _/ / /    | |/ /| | | (_| | (_| | (_) | | | \__ \ | |_) |  __/ | | | |  __/ | |  __/_ 
        #  |_||_|/_/_/     |___/ |_|  \__,_|\__, |\___/|_| |_|___/ |_.__/ \___| |_| |_|\___|_|  \___( )
        #                                    __/ |                                                  |/ 
        #                                   |___/                                                      
        if not(len(self.lastRequestState) > 0):
            self.lastRequestState = tablesRequestResponse

            self.lastRequestState = tablesRequestResponse
            # Doing app updating;
            GLOBALUSERDATA = tablesRequestResponse
            # Clearing the table buttons;
            self.destroyAllTableButtonsF()
            # Re-Loading all the table buttons;
            self.renderTablesF()
            # Re-loading the takeAway Count;
            self.showTakeAwayCountOnTakeAwayButtonF()
        else:
            if not(self.lastRequestState == tablesRequestResponse):
                self.lastRequestState = tablesRequestResponse
                # Doing app updating;
                GLOBALUSERDATA = tablesRequestResponse
                # Clearing the table buttons;
                self.destroyAllTableButtonsF()
                # Re-Loading all the table buttons;
                self.renderTablesF()
                # Re-loading the takeAway Count;
                self.showTakeAwayCountOnTakeAwayButtonF()
        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        

    # Buttons click this and the clicked table buttons table menu gets showed;
    def viewDesiredTableByTableButton(self, clickerBtn):
        self.CurrentBillingScreen = BillingScreen(clickerBtn)

    # Only gets started once, the timer for constantly sending requests to the server
    def startRequestTimerF(self):
        self.requestTimer = QTimer(self)
        self.requestTimer.timeout.connect(self.sendServerRequestF) # Here be dragons;
        self.requestTimer.start(1000) # Setting the one second delay;



# Products Screen;
class ProductsScreen(qtw.QWidget):
    def __init__(self):
        super().__init__()
        aa = qtw.QPushButton("ProductsScreen", self, clicked=lambda: self.goBackF())
        aa.move(100, 100)


        #========================================================================================================================
    def goBackF(self):
        appStack.setCurrentIndex(gotoMainWindowINDEX)



# Settings Screen;
class SettingsScreen(qtw.QWidget):
    def __init__(self):
        super().__init__()
        aa = qtw.QPushButton("settings", self, clicked=lambda: self.goBackF())
        aa.move(100, 100)


        #========================================================================================================================
    def goBackF(self):
        appStack.setCurrentIndex(gotoMainWindowINDEX)



# Statistics Screen;
class StatisticsScreen(qtw.QWidget):
    def __init__(self):
        super().__init__()
        # Screen Data;

        # State data;
        self.allDaysMonthsDatesScrollerButtons = []
        self.plottingDialogBoxExistsBool       = False

        # Loading the settings
        with open("./Data/settings.json") as settingsFile:
            self.SETTINGS = json.load(settingsFile)["globalData"]


        # Header;
        headerFrame = qtw.QFrame(self)
        headerFrame.setStyleSheet("background-color: gray;")
        headerFrame.setFixedSize(adakPV(100, "w", app), adakPV(8, "h", app))
        headerFrame.move(0, 0)

        # Go back button;
        goBackButton = qtw.QPushButton("Back", self, clicked=self.goBackF)
        goBackButton.setFixedSize(adakPV(8, "w", app), adakPV(5, "h", app))
        goBackButton.setFont(qtg.QFont("Arial", adakPV(1, "w", app)))
        goBackButton.setObjectName("goBackButton")
        goBackButton.move(adakPV(88, "w", app), adakPV(1.5, "h", app))

        # Date/Company name location;
        # Shadow for the name location;
        shadow = qtw.QGraphicsDropShadowEffect()
        shadow.setBlurRadius(30)
        shadow.setColor(qtg.QColor("white"))
        self.headerDateAndRestaurantNameLabel = qtw.QLabel("MM/DD/YYYY - RESTAURANTNAME                   ", headerFrame)
        self.headerDateAndRestaurantNameLabel.setFont(qtg.QFont("Arial", 30))
        self.headerDateAndRestaurantNameLabel.setStyleSheet("color: white")
        self.headerDateAndRestaurantNameLabel.setGraphicsEffect(shadow)
        self.headerDateAndRestaurantNameLabel.move(adakPV(1, "w", app), adakPV(2, "h", app))
        # Calling the set date function;
        self.setHeaderDataF()

        # Actual frame of the statistics screen;
        backgroundFrame = qtw.QFrame(self)
        backgroundFrame.setFixedSize(adakPV(100, "w", app), adakPV(92, "h", app))
        backgroundFrame.setObjectName("backgroundFrame")
        backgroundFrame.move(0, adakPV(8, "h", app))

        # Buttons/Controls/Settings frame;
        self.buttonsControlsSettingsFrame = qtw.QFrame(self)
        self.buttonsControlsSettingsFrame.setFixedSize(adakPV(22, "w", app), adakPV(70, "h", app))
        self.buttonsControlsSettingsFrame.setObjectName("buttonsControlsSettingsFrame")
        self.buttonsControlsSettingsFrame.move(adakPV(4, "w", app), adakPV(11, "h", app))

        # Statistics frame;
        self.StatisticsFrame = qtw.QFrame(self)
        self.StatisticsFrame.setFixedSize(adakPV(66, "w", app), adakPV(70, "h", app))
        self.StatisticsFrame.setObjectName("StatisticsFrame")
        self.StatisticsFrame.move(adakPV(30, "w", app), adakPV(11, "h", app))

        # Creating a line in "Buttons/Controls/Settings" frame for seperating the control buttons from settings;
        frameSeperatorLineF(self, adakPV(5, "w", app), adakPV(30, "h", app), adakPV(20, "w", app), adakPV(0.25, "w", app), color="white")

        # Command buttons;
        self.commandButtonsSCROLLER = qtw.QScrollArea(self)
        self.commandButtonsSCROLLER.setWidgetResizable(True)
        self.commandButtonsWIDGETCONTENTS = qtw.QWidget()
        self.commandButtonsSCROLLER.setObjectName("commandButtonsSCROLLER")
        self.commandButtonsSCROLLER.setFixedSize(adakPV(22, "w", app), adakPV(20, "h", app))
        self.commandButtonsSCROLLER.move(adakPV(4, "w", app), adakPV(11, "h", app))
        self.commandButtonsGRID = qtw.QGridLayout(self.commandButtonsWIDGETCONTENTS)
        self.commandButtonsSCROLLER.setWidget(self.commandButtonsWIDGETCONTENTS)
        self.commandButtonsGRID.setRowStretch(4, 1)
        # Calling the function for adding the command buttons to the grid;
        self.addButtonsToCommandsGrid()

        # Statistic settings information label;
        statisticInfoLabel = qtw.QLabel("Statistic Type:\n\nDaily Gap:\n\nStatistic Color:\n\nStatistic Thickness:\n\nShow Legend:", self)
        statisticInfoLabel.setFont(qtg.QFont("Arial", adakPV(0.9, "w", app)))
        statisticInfoLabel.setStyleSheet("color: white;")
        statisticInfoLabel.move(adakPV(4, "w", app)+10, adakPV(32, "h", app))

        # Statistc settings placements;
        self.loadStatisticsSettingsButttons();


        # Stylesheet;
        with open("./Data/Styles/StatisticsScreen.css") as rfss:
            self.setStyleSheet(rfss.read())


        #========================================================================================================================
    def goBackF(self):
        appStack.setCurrentIndex(gotoMainWindowINDEX)

    # The function for setting the values of the header data;
    def setHeaderDataF(self):
        self.headerDateAndRestaurantNameLabel.setText(str(time.strftime('%m/%d/%Y')) + " | Statistics/" + self.SETTINGS["restaurantName"])  # Cant use the f string arg as sublime is weird and makes weird highlightings;

    # The function for adding all the command buttons to the commandButtonsGrid;
    #QtGui.QColor(240, 53, 218)
    #QtGui.QColor(61, 217, 245)
    def addButtonsToCommandsGrid(self):
        # Colors
        c1 = qtg.QColor(175, 125, 241)
        c2 = qtg.QColor(61, 217, 245)

        # Button Size;
        buttonWidth = adakPV(10, "w", app)
        buttonHeight = adakPV(6, "h", app)


        # Buttons
        datesButton             = AnimatedButton(self, c1, c2, buttonWidth, buttonHeight, "Dates")
        viewFilesButton         = AnimatedButton(self, c1, c2, buttonWidth, buttonHeight, "View Files")
        allTimeEarningGraph     = AnimatedButton(self, c1, c2, buttonWidth, buttonHeight, "All Time Statistics")
        productsIndividualGraph = AnimatedButton(self, c1, c2, buttonWidth, buttonHeight, "Products\n Individual Graph")
        
        # Adding functions to the buttons;
        datesButton.clicked.connect(self.viewAllDatesForStatisticsF)
        #viewFilesButton.clicked.connect()
        #allTimeEarningGraph.clicked.connect()
        #productsIndividualGraph.clicked.connect()




        # Adding the buttons to the grid;
        self.commandButtonsGRID.addWidget(datesButton, 0, 0)
        self.commandButtonsGRID.addWidget(viewFilesButton, 1, 0)
        self.commandButtonsGRID.addWidget(allTimeEarningGraph, 0, 1)
        self.commandButtonsGRID.addWidget(productsIndividualGraph, 1, 1)


    # The function for rendering all the statistic settings comboboxes/buttons/spinboxes/check buttons;
    def loadStatisticsSettingsButttons(self):
        # Creating all the inputs;
        statisticTypeComboBoxOPTIONS = ["Line Graph", "Bar Chart"]
        self.statisticTypeComboBox = qtw.QComboBox(self)
        self.statisticTypeComboBox.setFixedSize(adakPV(10, "w", app), adakPV(3, "h", app))
        self.statisticTypeComboBox.addItems(statisticTypeComboBoxOPTIONS)
        self.statisticTypeComboBox.setFont(qtg.QFont("Arial", adakPV(1, "w", app)))
        #
        self.dailyGapSpinBox = qtw.QSpinBox(self)
        self.dailyGapSpinBox.setFixedSize(adakPV(10, "w", app), adakPV(3, "h", app))
        self.dailyGapSpinBox.setFont(qtg.QFont("Arial", adakPV(1, "w", app)))
        self.dailyGapSpinBox.setRange(1, 100)
        #
        self.statisticColorsComboBox = qtw.QComboBox(self)
        self.statisticColorsComboBox.setFixedSize(adakPV(10, "w", app), adakPV(3, "h", app))
        self.statisticColorsComboBox.addItems(COLORS)
        self.statisticColorsComboBox.setFont(qtg.QFont("Arial", adakPV(1, "w", app)))
        #
        self.statisticsThicknessSpinBox = qtw.QSpinBox(self)
        self.statisticsThicknessSpinBox.setFixedSize(adakPV(10, "w", app), adakPV(3, "h", app))
        self.statisticsThicknessSpinBox.setFont(qtg.QFont("Arial", adakPV(1, "w", app)))
        self.statisticsThicknessSpinBox.setRange(1, 10)
        #
        self.viewLegendCheckBox = adakCheckButton(self, adakPV(3, "h", app), adakPV(3, "h", app))

        # Placing all the inputs;
        self.statisticTypeComboBox.move(adakPV(15, "w", app), adakPV(32, "h", app))
        self.dailyGapSpinBox.move(adakPV(15, "w", app), adakPV(36, "h", app))
        self.statisticColorsComboBox.move(adakPV(15, "w", app), adakPV(40, "h", app)+5)
        self.statisticsThicknessSpinBox.move(adakPV(15, "w", app), adakPV(45, "h", app))
        self.viewLegendCheckBox.move(adakPV(15, "w", app), adakPV(50, "h", app))



    # The function for creating an overlay frame on top of the settings/buttons location;
    # This will be called before all the other specific-statistics functions which need extra space on the screen;
    def createOverSettingsOverlayFrameF(self):
        self.settingsOverlayFrame = qtw.QFrame(self)
        self.settingsOverlayFrame.setFixedSize(self.buttonsControlsSettingsFrame.width(), adakPV(80, "h", app))
        self.settingsOverlayFrame.setObjectName("settingsOverlayFrame")
        self.settingsOverlayFrame.move(self.buttonsControlsSettingsFrame.x(), self.buttonsControlsSettingsFrame.y())

    # The function for destroying the destroyOverSettingsOverlayFrameF;
    # Only to be called if OverSettingsOverlayFrameF is called before/exists;
    def destroyOverSettingsOverlayFrameF(self):
        self.clearMonthsDaysDatesGRIDF()
        self.settingsOverlayFrame.setParent(None)


    # This is the parent function for viewing the statistics by dates;
    def viewAllDatesForStatisticsF(self):
        # Creating the background frame;
        self.createOverSettingsOverlayFrameF()
        # Loading the dates/sorting them;
        self.loadAllDatesForViewingDateStatisticsF()
        # The function for loading the gui stuff on the settingsOverlayFrame;
        self.renderSettingsOverlayFrameGUISTUFFDDATES()
        # Rendering the months/days scroller data, as its the first load, loading it with months;
        self.renderDataOnTheMonthsDaysDatesScrollerF("m")

        

    # The function for loading the data for the dates scroller;
    # This function just loads and sorts the data, the rendering is done by another function;
    # Caller = datesButton;
    def loadAllDatesForViewingDateStatisticsF(self):
        self.allDatesUnsorted = []  # Creating an array keeping all the times of the files;
                                    # This will be unsorted, the data will then be sorted and properly put on date arrays;
                                    # The arrays post-sort will be: Monthly->Daily->Day Sales;
                                    # The method of storing is converting the data from string to time.strptime,
                                    # this way, the times will be sortable and certain info's (month/day) will be sortable too; 
                                    # This will improve the user experience and make it easier to navigate;
        # loading all the dates to the array;
        for file in os.listdir("./Data/Sales/AllDoneBills"):
            if file.endswith(".json"):
                self.allDatesUnsorted.append(time.strptime(file[:len(file)-5], "%m-%d-%Y-%H-%M-%S"))
        
        # Sorting the months;
        # Creating an array called "onlyMonthsSorted" which will have arrays of days in it,
        # Those arrays will represent months, the first element of the array will be the date keeping the month/year;
        # The other elements will be the days of the month;
        self.onlyMonthsSorted = []
        self.sortUnsortedDatesArrayToMonthsF()
        # Sorting the days, same logic as onlyMonthsSorted;
        self.onlyDaysSorted = []
        self.sortUnsortedDatesArrayToDaysF()
        # Sorting the data completely now;
        self.sortDataCompletelyAfterMonthsAndDaySortF()
        # After the sort, self.onlyMonthsSorted will become the fully sorted array;
        # Keep That in mind;
        # The other arrays [self.allDatesUnsorted, self.onlyDaysSorted] are not usefull anymore, so we can dereference/clear them;
        self.allDatesUnsorted.clear()
        self.onlyDaysSorted.clear()

        
    # The function for sorting the unsorted dates array;
    # This only sorts the months in the unsorted array, for sorting the data to day logic, another function is used;
    def sortUnsortedDatesArrayToMonthsF(self):
        for unsortedDate in self.allDatesUnsorted: # Looping through all the unsorted dates;
                monthHasBeenFoundInArray = False   # The variable that determines wether or not the month is in self.onlyMonthsSorted;
                                                   # This only becomes true if the current index item of the self.allDatesUnsorted array has the same month/year as the current index of the sorted array;
                                                   # If it is true, it means the unsorted value is in the sorted array so there is no need to add it to the sorted array again,
                                                   # so the value becomes true, and the loop breaks;
                                                   # Otherwise, if no items are found matching the unsorted index in the sorted array, the item is added to the sorted array;
                for checkMonthArrLOOPCHECKER in self.onlyMonthsSorted:
                    if checkMonthArrLOOPCHECKER[0] == f"{unsortedDate.tm_mon}-{unsortedDate.tm_year}":
                        monthHasBeenFoundInArray = True
                        break
                if not(monthHasBeenFoundInArray):
                    self.onlyMonthsSorted.append([f"{unsortedDate.tm_mon}-{unsortedDate.tm_year}"])
   
    # The same logic as sortUnsortedDatesArrayToMonthsF, just for days;
    def sortUnsortedDatesArrayToDaysF(self):
        for unsortedDay in self.allDatesUnsorted: # Looping through all the unsorted dates;
            dayHasBeenFoundInArray = False

            for checkDay in self.onlyDaysSorted:
                if checkDay[0] == f"{unsortedDay.tm_mon}-{unsortedDay.tm_mday}-{unsortedDay.tm_year}":
                    checkDay.append(unsortedDay)
                    dayHasBeenFoundInArray = True
                    break

            if not(dayHasBeenFoundInArray):
                self.onlyDaysSorted.append([f"{unsortedDay.tm_mon}-{unsortedDay.tm_mday}-{unsortedDay.tm_year}"])
    # The function for sorting the data completely;
    def sortDataCompletelyAfterMonthsAndDaySortF(self):
        for day in self.onlyDaysSorted:
            for month in self.onlyMonthsSorted:
                dayTime   = time.strptime(day[0], "%m-%d-%Y")
                monthTime = time.strptime(month[0], "%m-%Y")
                if dayTime.tm_mon == monthTime.tm_mon:
                    month.append(day)


    # The function for rendering the months/days specific buttons on the dates scroller;
    # It takes the rendering method, which is either month or day, 
    # and monthIndex, which is only used if the rendertype is "d" (days);
    # Based of that, it makes it able for the user to view the stats of a specific day with the click of a button;
    # Rendertype can either me "m"->months || "d"->days;
    def renderDataOnTheMonthsDaysDatesScrollerF(self, renderType, monthIndex=None):
        if renderType == "m":
            # MONTHS;

            # Setting the render info label properly
            self.currentViewStyleShowerLabel.setText("Months")

            rowIndex = 0
            for month in self.onlyMonthsSorted:

                # Creating a button with the dynamic data;
                monthButton = qtw.QPushButton(month[0])
                monthButton.setFixedSize(adakPV(18, "w", app), adakPV(4, "h", app)) # Setting fixed size;
                monthButton.clicked.connect(lambda ignore, propToPass=rowIndex: self.viewCertainMonthDaysF(propToPass))
                


                # Adding the month button to the buttons scroller grid;
                self.monthsDaysDatesGRID.addWidget(monthButton, rowIndex, 0) 
                # Adding the month button to the buttons list;
                self.allDaysMonthsDatesScrollerButtons.append(monthButton)
                # Incrementing the row index;
                rowIndex+=1


        else:
            # DAYS;

            # Setting the render info label properly
            self.currentViewStyleShowerLabel.setText("Days")
            print(self.onlyMonthsSorted)
            x = 0
            y = 0
            index = 0
            for day in self.onlyMonthsSorted[monthIndex][1:len(self.onlyMonthsSorted[monthIndex])]:
                if y > 1:
                    y = 0
                    x += 1
                # Creating a button with the dynamic data;
                dayButton = qtw.QPushButton(str(day[0]))
                dayButton.setFixedSize(adakPV(9, "w", app), adakPV(4, "h", app)) # Setting fixed size;
                #dayButton.clicked.connect(lambda ignore, propToPass=index: self.viewCertainMonthDaysF(propToPass))
                


                # Adding the month button to the buttons scroller grid;
                self.monthsDaysDatesGRID.addWidget(dayButton, x, y) 
                # Adding the month button to the buttons list;
                self.allDaysMonthsDatesScrollerButtons.append(dayButton)
                    
                # Incrementing the column;
                y+=1
                # Incrementing the index;
                index+=1

            # On days scroller call, creating a "Go to months" button as well, it will be placed over the scroller at its bottom;
            self.goToMonthsButton = qtw.QPushButton("Back To Months", self.settingsOverlayFrame, clicked=self.viewMonthsFromDaysF)
            self.goToMonthsButton.setFixedSize(adakPV(8, "w", app), adakPV(4, "h", app))
            self.goToMonthsButton.setFont(qtg.QFont("Arial", adakPV(0.7, "w", app)))
            self.goToMonthsButton.setObjectName("goBackButton")
            self.goToMonthsButton.move(adakPV(7, "w", app), adakPV(49, "h", app))
            self.goToMonthsButton.show()



    # The function for viewing a certain months days;
    # This doesnt render or clear or do anything, this is just the parent function for all those functions;
    def viewCertainMonthDaysF(self, monthIndex):
        # Checking if the viewWholeMonthStatisticsCheckBox is checked;
        # If it is checked, not showing the days of the month, instead, plotting the statistics of the whole month;
        if not(self.viewWholeMonthStatisticsCheckBox.isChecked):
            # Clearing the scroller;
            self.clearMonthsDaysDatesGRIDF()
            # Clearing the month specific gui;
            self.clearGuiMonthViewSpecific()
            # Rendering the month days;
            self.renderDataOnTheMonthsDaysDatesScrollerF("d", monthIndex)
        else:
            # The client has checked the viewWholeMonthStatisticsCheckBox, 
            # which means the statistics of the whole month have to be rendered;
            # For that, not rendering the days, instead, 
            # calling the renderWholeChosenMonthStatisticsF with self.onlyMonthsSorted's (monthIndex) indexed data/month name being passed as a parameter;
            self.renderWholeChosenMonthStatisticsF(self.onlyMonthsSorted[monthIndex][0])


    # The function for going from days back to months;
    def viewMonthsFromDaysF(self):
        # Clearing the scroller;
        self.clearMonthsDaysDatesGRIDF()
        # Removing the day based on screen data;
        self.goToMonthsButton.setParent(None)
        # Re-Showing the month specific settings;
        self.showGuiMonthViewSpecific()
        # Rendering the month days;
        self.renderDataOnTheMonthsDaysDatesScrollerF("m")




    # The function for clearing the MonthsDaysDatesGRID and dereferencing all the data associated with it;
    def clearMonthsDaysDatesGRIDF(self):
        # Firstly, clearing the scroller;
        for button in self.allDaysMonthsDatesScrollerButtons:
            button.setParent(None)
        # Clearing the array;
        self.allDaysMonthsDatesScrollerButtons.clear()


    # This function renders data specifically for use while still on the months-part of the scroller;
    def renderGuiMonthViewSpecific(self):
        # NOTE: DONT FORGET TO ADD THE VALUES ADDED HERE TO THE FUNCTIONS:
        # {showGuiMonthViewSpecific and clearGuiMonthViewSpecific} properly;

        # Rendering the text for options;
        self.guiMonthSpecificOptionsLabel = qtw.QLabel("View whole month Statistics:\n", self.settingsOverlayFrame)
        self.guiMonthSpecificOptionsLabel.setFont(qtg.QFont("Arial", adakPV(1, "w", app)))
        self.guiMonthSpecificOptionsLabel.move(adakPV(1, "w", app), adakPV(52, "h", app))
        self.guiMonthSpecificOptionsLabel.show()

        # Creating the options;
        self.viewWholeMonthStatisticsCheckBox = adakCheckButton(self.settingsOverlayFrame, adakPV(3, "h", app), adakPV(3, "h", app))

        # Locating the options;
        self.viewWholeMonthStatisticsCheckBox.move(adakPV(18, "w", app), adakPV(52, "h", app))

        # Showing the options
        self.viewWholeMonthStatisticsCheckBox.show()



        

    # This function hides the data specifically for use while still on the months-part of the scroller;
    def clearGuiMonthViewSpecific(self):
        self.guiMonthSpecificOptionsLabel.setVisible(False)
        self.viewWholeMonthStatisticsCheckBox.setVisible(False)

    def showGuiMonthViewSpecific(self):
        self.guiMonthSpecificOptionsLabel.setVisible(True)
        self.viewWholeMonthStatisticsCheckBox.setVisible(True)



    # This function shows the statistics of the whole month;
    # The logic is the same as: (renderChosenDayStatisticsF),
    # So not writing extensive commenting about the function;
    def renderWholeChosenMonthStatisticsF(self, monthNameParameter):
        # First, checking if monthNameParameter is a proper length:
        if len(monthNameParameter) == 6:
            monthNameParameter = "0" + monthNameParameter

        wholeMonthStatsArr   = []
        wholeMonthSalesPrice = 0
        # Looping through all files in the AllDoneBills directory,
        # if the month and year (String slicing and working) is the same as the current month given by the monthDayDataArrayParameter,
        # properly adding the values in the file to the wholeMonthStatsArr array;
        for allDoneBill in os.listdir("./Data/Sales/AllDoneBills"):
            # Checking if the month is proper;
            if allDoneBill[0:2] == monthNameParameter[0:2]:
                # Checking if the year is proper;
                if allDoneBill[6:10] == monthNameParameter[3:len(monthNameParameter)]:
                    # Reading the file and then, adding the values to the wholeMonthStatsArr;
                    with open(f"./Data/Sales/AllDoneBills/{allDoneBill}") as donebilloaderfile:
                        doneBillFile = json.load(donebilloaderfile)

                    # First, incrementing the price of the "wholeMonthSalesPrice" variable;
                    wholeMonthSalesPrice += doneBillFile["tbp"]

                    # Going through all the table items and adding/incrementing them in the wholeMonthStatsArr based off their count;
                    for billItem in doneBillFile["tBill"]:
                        # Checking if the billItem exists in the wholeMonthStatsArr;
                        billItemExistsInWholeMonthStatsArr = False
                        wholeMonthStatsArrLoopIndex = 0
                        for monthStatItem in wholeMonthStatsArr:
                            if monthStatItem["n"] == billItem["n"]:
                                billItemExistsInWholeMonthStatsArr = True
                                break
                            wholeMonthStatsArrLoopIndex+=1

                        # If the item billItem exists in the wholeMonthsArr, billItemExistsInWholeMonthStatsArr will be True,
                        # In that case, incrementing the "c" (count) and "p" (price) of the wholeMonthsArr[wholeMonthStatsArrLoopIndex];
                        # The reason for also incrementing the price is simply showing the client how much they earnt from a certain product;
                        if billItemExistsInWholeMonthStatsArr:
                            wholeMonthStatsArr[wholeMonthStatsArrLoopIndex]["c"] += billItem["c"]
                            wholeMonthStatsArr[wholeMonthStatsArrLoopIndex]["p"] += billItem["p"]
                        else:
                            wholeMonthStatsArr.append(billItem)

        # The whole months array and whole months sale price is ready now;
        # Creating the plot widget;
        if not(self.plottingDialogBoxExistsBool):
            self.plottingDialogBoxExistsBool = True
            self.showPlotsF(wholeMonthStatsArr, wholeMonthSalesPrice)





    # This function shows the statistics of chosen days,
    # It gets called by a "day" scroller;
    # It takes the chosen day's string name as a parameter;
    # It then goes through all the files in the AllDoneBills directory,
    # And those that were created on a proper (required/wanted) day scheme have their values collected;
    def renderChosenDayStatisticsF(self, dayDataArrayParameter):
        print(dayDataArrayParameter)
        

    # As plots cant be sized easily, just creating a function where a new dialog box pops up;
    # The dialog gets the "stays on top hint".
    # The dialog box will also get its titlebar removed and it will be sized/places exactly on the stats location;
    # So it will feel just like a "same screen" widget;
    def showPlotsF(self, plotingArray, totalPrice):
        # Creating a QDialogBox;
        # Creating it as an instance as it will be accessed/edited/deleted from other functions as well;
        self.plottingDialogBox = qtw.QDialog(self)
        self.plottingDialogBox.setFixedSize(self.StatisticsFrame.width(), self.StatisticsFrame.height())
        self.plottingDialogBox.setObjectName("plottingDialogBox")



        # NOTE



        # Setting the plotting dialog's window flags;
        self.plottingDialogBox.setWindowFlags(qtc.Qt.WindowStaysOnTopHint | qtc.Qt.FramelessWindowHint)

        # Moving the plotting dialog to the same location as the statistics frame;
        self.plottingDialogBox.move(self.StatisticsFrame.x(), self.StatisticsFrame.y())

        # Showing the plotting dialog;
        self.plottingDialogBox.show()


    # This function renders all the gui of the settingsOverlayFrame for dates viewing;
    # Its strictly called renderSettingsOverlayFrameGUISTUFFDDATES as there are other gui rendering functions for other statistics viewings as well;
    def renderSettingsOverlayFrameGUISTUFFDDATES(self):
        # Creating a label saying "dates statistics";
        datesStatisticsInfoLabel = qtw.QLabel("Dates Statistics", self.settingsOverlayFrame)
        datesStatisticsInfoLabel.setFont(qtg.QFont("Arial", adakPV(1, "w", app)))
        datesStatisticsInfoLabel.move(adakPV(7, "w", app), adakPV(1, "h", app))

        # Horizontal on-scroller seperator lines;
        frameSeperatorLineF(self.settingsOverlayFrame, adakPV(4, "w", app), adakPV(4, "h", app), adakPV(14, "w", app), 3)
        frameSeperatorLineF(self.settingsOverlayFrame, adakPV(4, "w", app), adakPV(8, "h", app), adakPV(14, "w", app), 3)


        # The months/Days Scroller;
        self.monthsDaysDatesSCROLLER = qtw.QScrollArea(self.settingsOverlayFrame)
        self.monthsDaysDatesSCROLLER.setWidgetResizable(True)
        self.monthDaysDatesContents = qtw.QWidget()
        self.monthsDaysDatesSCROLLER.setObjectName("monthsDaysDatesSCROLLER")
        self.monthsDaysDatesSCROLLER.setFixedSize(adakPV(22, "w", app), adakPV(41, "h", app))
        self.monthsDaysDatesSCROLLER.move(0, adakPV(10, "h", app))
        self.monthsDaysDatesGRID = qtw.QGridLayout(self.monthDaysDatesContents)
        self.monthsDaysDatesSCROLLER.setWidget(self.monthDaysDatesContents)
        self.monthsDaysDatesGRID.setRowStretch(4, 1)


        # Go Back Button;
        goBackButton = qtw.QPushButton("Back", self.settingsOverlayFrame, clicked=self.destroyOverSettingsOverlayFrameF)
        goBackButton.setFixedSize(adakPV(8, "w", app), adakPV(5, "h", app))
        goBackButton.setFont(qtg.QFont("Arial", adakPV(1, "w", app)))
        goBackButton.setObjectName("goBackButtonOverlayFrame")
        goBackButton.move(adakPV(7, "w", app), adakPV(74, "h", app))

        # The current style of viewing shower label;
        # This will only be edited in the render buttons function;
        # That way, it be set either "Months" or "Days" properly based of the given parameter;
        self.currentViewStyleShowerLabel = qtw.QLabel("AAAAAAAAA", self.settingsOverlayFrame)
        self.currentViewStyleShowerLabel.setFont(qtg.QFont("Arial", adakPV(1, "w", app)))
        self.currentViewStyleShowerLabel.move(adakPV(10, "w", app), adakPV(5, "h", app))

        # Rendering the month specific settings, it will become invincibile while on days and vice versa;
        self.renderGuiMonthViewSpecific()






        # Showing is done after the gui is created;
        self.settingsOverlayFrame.show()



# Billing Screen;
class BillingScreen(qtw.QDialog):
    def __init__(self, curTabIndex):
        super().__init__()
        # State Data;
        self.allCategoriesButtons              = []          # The buttons on the left side, working for the categories data;
        self.lastBillState                     = {}          # This will keep the last state of the bill so the app can know if it should refresh the bill or not;
        self.billProductButtons                = []          # The dynamically created buttons of the bill items;
        self.totalBillPrice                    = 0           # Instance of the current bill's price;
        self.currentTableINDEX                 = curTabIndex # Instance of the current table index;
        self.allProductsButtons                = []          # The buttons on the left side, working for the products data;
        self.DELETEDELIVEREDCANCELWIDGETEXISTS = False       # Shows if the deleteDeliveredCancelWIDGET exists;
        self.DELETETRANSACTIONWIDGETEXSTS      = False       # Shows if the delete transaction widget exists;

        # Creating the design;
        # Fetching the tables bill data and also starting a constant fetch to the server via a timer
        self.fetchBillDataF(curTabIndex)

        # Loading the categories to the "self.CategoriesArr" array;
        self.loadProductCategoriesF()


        # Left dark categories/products background;
        leftBackgroundFrame = qtw.QFrame(self)
        leftBackgroundFrame.setFixedSize(adakPV(60, "w", app), adakPV(100, "h", app))
        leftBackgroundFrame.setStyleSheet("background-color: #333;")
        leftBackgroundFrame.move(0, 0)

        # Right gray payments location background;#c3c3c3
        rightBackgroundFrame = qtw.QFrame(self)
        rightBackgroundFrame.setFixedSize(adakPV(40, "w", app), adakPV(100, "h", app))
        rightBackgroundFrame.setStyleSheet("background-color: #c3c3c3;")
        rightBackgroundFrame.move(adakPV(60, "w", app), 0)

        # Categories/products Frame;
        categoriesBackgroundFrame = qtw.QFrame(self)
        categoriesBackgroundFrame.setFixedSize(adakPV(56, "w", app), adakPV(85, "h", app))
        categoriesBackgroundFrame.setStyleSheet("background-color: #333; border: 3px solid #7f7f7f;")
        categoriesBackgroundFrame.move(adakPV(2, "w", app), adakPV(3, "h", app))


        # Categories/Products Text;
        self.catOrProdHeaderText = qtw.QLabel("Categories                                                       ", self)
        self.catOrProdHeaderText.setStyleSheet("color: white;")
        self.catOrProdHeaderText.setFont(qtg.QFont("Arial", adakPV(2, "w", app)))
        self.catOrProdHeaderText.move(adakPV(24, "w", app), adakPV(3.9, "h", app))


        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


        # Products/Categories scroller grid;
        self.prodOrCatScroller = qtw.QScrollArea(self)
        self.prodOrCatScroller.setWidgetResizable(True)
        self.scrollAreaWidgetContents = qtw.QWidget()
        self.prodOrCatScroller.setStyleSheet("background-color: #333; border: 2px solid #7f7f7f;")
        self.prodOrCatScroller.setFixedSize(adakPV(56, "w", app), adakPV(78, "h", app))
        self.prodOrCatScroller.move(adakPV(2, "w", app), adakPV(10, "h", app))
        self.prodOrCatGrid = qtw.QGridLayout(self.scrollAreaWidgetContents)
        self.prodOrCatScroller.setWidget(self.scrollAreaWidgetContents)
        
        # Loading the categories;
        self.renderProductCategoriesF()


        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


        # Total and Total with tax holder frame;
        totalFrame = qtw.QFrame(self)
        totalFrame.setStyleSheet("background-color: #a249a4; border: 1px solid black;")
        totalFrame.setFixedSize(adakPV(32, "w", app), adakPV(8, "h", app))
        totalFrame.move(adakPV(64, "w", app), adakPV(62, "h", app))
        
        # Total frame seperator;
        seperatorLineF(self, 80, 62, 0.25, 16, app)

        # Total Label;
        aaaaa = qtw.QLabel("Total:", self)
        aaaaa.setStyleSheet("color: white;")
        aaaaa.setFont(qtg.QFont("Arial", int(adakPV(1, "w", app)*1.2)))
        aaaaa.move(adakPV(64.5, "w", app), adakPV(63, "h", app))

        self.totalLabel = qtw.QLabel("----------------------------------------------------------------", self)
        self.totalLabel.setStyleSheet("color: white;")
        self.totalLabel.setFont(qtg.QFont("Arial", int(adakPV(1, "w", app)*1.2)))
        self.totalLabel.move(adakPV(64.5, "w", app), adakPV(66, "h", app))

        # Total with TVSH label;
        bbbbb = qtw.QLabel("Total me TVSH:", self)
        bbbbb.setStyleSheet("color: white;")
        bbbbb.setFont(qtg.QFont("Arial", int(adakPV(1, "w", app)*1.2)))
        bbbbb.move(adakPV(80.5, "w", app), adakPV(63, "h", app))

        self.totalWithTVSH = qtw.QLabel("----------------------------------------------------------------", self)
        self.totalWithTVSH.setStyleSheet("color: white;")
        self.totalWithTVSH.setFont(qtg.QFont("Arial", int(adakPV(1, "w", app)*1.2)))
        self.totalWithTVSH.move(adakPV(80.5, "w", app), adakPV(66, "h", app))


        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


        # Go Back Button;
        goBackButton = qtw.QPushButton("ᐊ Back", self, clicked=lambda: self.goBackF()) # FUCK MY LIFE.
        goBackButton.setStyleSheet("background-color: red; color: white")
        goBackButton.setFont(qtg.QFont("Arial", int(adakPV(1.9, "w", app)/1.5)))
        goBackButton.setFixedSize(adakPV(10, "w", app), adakPV(6, "h", app))
        goBackButton.move(adakPV(89, "w", app), adakPV(1, "h", app))

        # Current tabel text;
        currentTableLabel = qtw.QLabel(f"Table {str(curTabIndex+1)}", self)
        currentTableLabel.setFont(qtg.QFont("Arial", adakPV(2, "w", app)))
        #currentTableLabel.setStyleSheet("color: white;")
        currentTableLabel.move(adakPV(75, "w", app), adakPV(2, "h", app))

        # Bill Products scroller;
        self.billProductsScrollArea = qtw.QScrollArea(self)
        self.billProductsScrollArea.setWidgetResizable(True)
        self.scrollAreaWidgetContents = qtw.QWidget()
        self.billProductsScrollArea.setStyleSheet("background-color: white; border: 1px solid black;")
        self.billProductsScrollArea.setFixedSize(adakPV(32, "w", app), adakPV(55, "h", app))
        self.billProductsScrollArea.move(adakPV(64, "w", app), adakPV(7.9, "h", app))
        self.billScrollerGrid = qtw.QGridLayout(self.scrollAreaWidgetContents)
        self.billProductsScrollArea.setWidget(self.scrollAreaWidgetContents)

        # Rendering the items to the bill;
        self.setBillPageDataProperlyPostServerRequestF()


        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


        # PayLocation center seperator;
        seperatorLineF(self, 80, 71, 0.33, 56, app)

        # New Products Count Label;
        newProductsCountLabel = qtw.QLabel("New Product Count:", self)
        newProductsCountLabel.setFont(qtg.QFont("Arial", adakPV(1.3, "w", app)))
        newProductsCountLabel.move(adakPV(64, "w", app), adakPV(70, "h", app))

        # New Products Count Entry;
        self.newProductsCountEntry = qtw.QLineEdit(self)
        self.newProductsCountEntry.setFixedSize(adakPV(14, "w", app), adakPV(3, "h", app))
        self.newProductsCountEntry.setFont(qtg.QFont("Arial", adakPV(1.2, "w", app)))
        self.newProductsCountEntry.setValidator(qtg.QIntValidator())
        self.newProductsCountEntry.setPlaceholderText("Amount of items:")
        self.newProductsCountEntry.move(adakPV(64, "w", app), adakPV(73.5, "h", app))
        
        
        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        

        # Paid amount label:
        paidAmounttLabel = qtw.QLabel("Paid Amount:", self)
        paidAmounttLabel.setFont(qtg.QFont("Arial", adakPV(1.3, "w", app)))
        paidAmounttLabel.move(adakPV(81, "w", app), adakPV(70, "h", app))

        # Paid amount entry:
        self.paidAmountEntry = qtw.QLineEdit(self)
        self.paidAmountEntry.setFixedSize(adakPV(8, "w", app), adakPV(3, "h", app))
        self.paidAmountEntry.setFont(qtg.QFont("Arial", adakPV(1.2, "w", app)))
        self.paidAmountEntry.setValidator(qtg.QDoubleValidator())
        self.paidAmountEntry.textChanged.connect(self.setViewPaidAmountAndChangeLabelAmounts)
        self.paidAmountEntry.move(adakPV(91, "w", app), adakPV(70, "h", app))

        # View Paid Amount Label
        self.viewPaidAmounttLabel = qtw.QLabel(">                                       ", self)
        self.viewPaidAmounttLabel.setFont(qtg.QFont("Arial", adakPV(1.3, "w", app)))
        self.viewPaidAmounttLabel.move(adakPV(81, "w", app), adakPV(73, "h", app))

        # Paid amount bottom seperator;
        seperatorLineF(self, 80, 76, 20, 0.5, app)

        # Change Label
        self.changeLabel = qtw.QLabel("Change:                         ", self)
        self.changeLabel.setFont(qtg.QFont("Arial", adakPV(1.3, "w", app)))
        self.changeLabel.move(adakPV(81, "w", app), adakPV(77, "h", app))
        seperatorLineF(self, 80, 80.5, 20, 0.5, app)

        # Change amount bottom seperator;

        # Transaction Button;
        doTransactionButton = qtw.QPushButton("Sell", self, clicked=self.tableTransactionF)
        doTransactionButton.setFixedSize(adakPV(8, "w", app), adakPV(5, "h", app))
        doTransactionButton.setFont(qtg.QFont("Arial", adakPV(1.5, "w", app)))
        doTransactionButton.setStyleSheet("background-color: green; color: white;")
        doTransactionButton.move(adakPV(86, "w", app), adakPV(83, "h", app))

        # Cancel Sale Button;
        cancelSaleButton = qtw.QPushButton("Cancel", self, clicked=self.cancelTransactionFunctionDANGEROUSF)
        cancelSaleButton.setFixedSize(adakPV(8, "w", app), adakPV(5, "h", app))
        cancelSaleButton.setFont(qtg.QFont("Arial", adakPV(1.5, "w", app)))
        cancelSaleButton.setStyleSheet("background-color: red; color: white;")
        cancelSaleButton.move(adakPV(86, "w", app), adakPV(92, "h", app))

        # The viewCategories Button
        self.viewCategoriesButton = qtw.QPushButton("View Categories", self, clicked=lambda: self.viewCategoriesF()) # FUCK MY LIFE.
        self.viewCategoriesButton.setStyleSheet("background-color: red; color: white")
        self.viewCategoriesButton.setFont(qtg.QFont("Arial", int(adakPV(1.9, "w", app)/1.5)))
        self.viewCategoriesButton.setFixedSize(adakPV(14, "w", app), adakPV(6, "h", app))
        self.viewCategoriesButton.move(adakPV(44, "w", app), adakPV(92, "h", app))
        self.viewCategoriesButton.setVisible(False)


        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        # The timer for asynchronously fetching the api and editing the data on the screen;
        self.singleBillFetchTimer = QTimer(self)
        self.singleBillFetchTimer.timeout.connect(lambda: self.fetchBillDataF(curTabIndex))
        self.singleBillFetchTimer.start(250) # Setting the one second delay;

        # Showing the app in full screen;
        self.setWindowFlags(qtc.Qt.WindowStaysOnTopHint)
        self.showFullScreen()
        #========================================================================================================================

    # The function for fetching all of the data in the current table's bill;
    def fetchBillDataF(self, curTabIndex):
        self.billProducts = req.post(f"{ServerUrl}singleTableData", data={"restaurantID": GLOBALUSERDATA["restaurantID"], "password": GLOBALUSERDATA["password"], "curTabIndex": curTabIndex}).json()
        # Checking if the request was accepted;
        if self.billProducts["validity"]:
            # Checking if we should set the last bill state;
            if not(len(self.lastBillState) > 0):
                self.lastBillState = self.billProducts["tablesData"]
            else:
                self.setBillPageDataProperlyPostServerRequestF()
        else:
            qtw.QMessageBox.critical(self, "Authentication error!", f"{self.billProducts['msg']}")


    def setBillPageDataProperlyPostServerRequestF(self):
        # Checking if the request is the same as the old bill state;
        if not(self.lastBillState == self.billProducts):
            # The values are different, so there was a change to the bill,
            # Based of this info, setting the last state to the current request state and re-rendering all the buttons/prices/info etc..;
            self.lastBillState = self.billProducts["tablesData"]

            # Clearing the buttons;
            self.destroyBillItemsF()

            # Creating new buttons;
            self.renderBillItemsF()
        else:
            # It's the same so not doing anything;
            pass


    def renderBillItemsF(self):
        x = 0
        toSetBillPrice = 0
        # reversed();
        for billItem in self.billProducts["tablesData"]["tBill"]: 
            # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            # Bill Item Keywords:'n': 'Tonic', 'p': 1, 'd': False, 'count': 1}
            #   n = name      | STRING |
            #   p = price     |   INT  | 
            #   d = delivered |  BOOL  |
            #   c = count     |   INT  |
            # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

            # Checking if the item is delivered, if it is settings its background color to orange;
            billItemFRAME = qtw.QFrame(self)
            billItemFRAME.setFixedSize(adakPV(30, "w", app), adakPV(4, "h", app))
            billItemFRAME.setStyleSheet("background-color: #efe4b0; border: 1px solid black; border-radius: 5;")

            # Creating the item data seperators;
            frameSeperatorLineF(billItemFRAME, int(billItemFRAME.width()*0.55), 0, int(billItemFRAME.width()//150), adakPV(4, "h", app))
            frameSeperatorLineF(billItemFRAME, int(billItemFRAME.width()*0.82), 0, int(billItemFRAME.width()//150), adakPV(4, "h", app))
            # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            # Item Info Datas
            itemNameLabel = qtw.QLabel(str(billItem["n"]), billItemFRAME)
            itemNameLabel.setFont(qtg.QFont("Arial", int(adakPV(1.5, "w", app)*0.8)))
            itemNameLabel.setFixedSize(int(billItemFRAME.width()*0.55), adakPV(4, "h", app))
            itemNameLabel.move(0, 0)

            itemPriceLabel = qtw.QLabel(f"{str(billItem['p'])}$", billItemFRAME)
            itemPriceLabel.setFont(qtg.QFont("Arial", int(adakPV(1.5, "w", app)*0.8)))
            itemPriceLabel.setFixedSize(int(billItemFRAME.width()*0.27), adakPV(4, "h", app))
            itemPriceLabel.move(int(billItemFRAME.width()*0.55), 0)

            itemCountLabel = qtw.QLabel(str(billItem["c"]), billItemFRAME)
            itemCountLabel.setFont(qtg.QFont("Arial", int(adakPV(1.5, "w", app)*0.8)))
            itemCountLabel.setFixedSize(int(billItemFRAME.width()*0.18), adakPV(4, "h", app))
            itemCountLabel.move(int(billItemFRAME.width()*0.82), 0)
            # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

            
            # Checking if the current item index has been delivered or not;
            # If it hasn't been delivered:
            #   Giving it the click popup for the "delivered/delete/cancel" functions;
            # If it has been delivered:
            #   Not giving it any functions and settings it background color to orange instead of yellow;
            if not(billItem["d"]):
                billItemFRAME.mousePressEvent = lambda state, index=x: self.deleteDeliveredCancelBillItemPopupFunction(index)
            else:
                billItemFRAME.setStyleSheet("background-color: #ff7f27; border: 1px solid black; border-radius: 10;")


            # Appending the item to the self.billProductButtons array;
            self.billProductButtons.append(billItemFRAME)

            # Adding the frame to the billScrollerGrid;
            self.billScrollerGrid.addWidget(billItemFRAME, x, 0)

            # Incrementing the toSetBillPrice;
            toSetBillPrice+=float(billItem["p"]*billItem["c"])

            # Incrementing the x / row;
            x+=1
        # As we are out of the loop, setting the total price/total price with tvsh + setting the instance bill price;
        self.totalBillPrice = toSetBillPrice
        self.totalLabel.setText(f"{str(round(toSetBillPrice, 2))}€")
        self.totalWithTVHSTEXTVALUE = str(round(toSetBillPrice-TVSHVALUEPERCENTAGE/100*toSetBillPrice, 2))
        self.totalWithTVSH.setText(f"{self.totalWithTVHSTEXTVALUE}€")


    # Function for destroying all the bill items from the bill;
    # Mainly for refreshes.
    def destroyBillItemsF(self):
        for billItem in self.billProductButtons:
            billItem.setParent(None)
        self.billProductButtons.clear()


    # The function for setting the self.viewPaidAmounttLabel's text to that of the paidAmountEntries text;
    def setViewPaidAmountAndChangeLabelAmounts(self):
        if len(self.paidAmountEntry.text()) > 0:
            if is_number(self.paidAmountEntry.text()):
                self.viewPaidAmounttLabel.setText(f"> {self.paidAmountEntry.text()}€")
                self.changeLabel.setText(f"Change: {str(round(float(self.paidAmountEntry.text())-self.totalBillPrice ,2))}€")
            else:
                qtw.QMessageBox.critical(self, "Value Error", "Only the charecters [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, '-', '.'] are allowed in the price entry;")            
                self.paidAmountEntry.setText(self.paidAmountEntry.text()[0:len(self.paidAmountEntry.text())-1])


    # The Delete/Delivered/Cancel popup function;
    def deleteDeliveredCancelBillItemPopupFunction(self, itemIndex):
        self.DELETEDELIVEREDCANCELWIDGETEXISTS = True

        # Getting the current mouse position;
        mouseX, mouseY = pyautogui.position()
        widthPercentage, heighPercentage = adakPV(16, "w", app), adakPV(16, "h", app)


        # Creating the the delivered/delete/cancel widget;
        self.deleteDeliveredCancelWIDGET = qtw.QDialog()
        self.deleteDeliveredCancelWIDGET.setObjectName("dodocWIDGET")

        
        # Checking if we should start it on the right or the left side of the curson, 
        # as if the mouse clicked somewhere near the edge of the screen the window might get out of the screen;
        if mouseX+widthPercentage >= app.primaryScreen().size().width():
            mouseX-=widthPercentage
        # Placing the frame;
        self.deleteDeliveredCancelWIDGET.setGeometry(mouseX, mouseY, widthPercentage, heighPercentage)

        # Placing the Delivered/Cancel/Delete buttons;
        deliveredButton = qtw.QPushButton("Delivered", self.deleteDeliveredCancelWIDGET, clicked=lambda: self.ProductFromBillDeliveredF(itemIndex))
        deliveredButton.setFixedSize(widgetPercentageValue(30, "w", self.deleteDeliveredCancelWIDGET), widgetPercentageValue(25, "h", self.deleteDeliveredCancelWIDGET))
        deliveredButton.move(widgetPercentageValue(10, "w", self.deleteDeliveredCancelWIDGET), widgetPercentageValue(15, "h", self.deleteDeliveredCancelWIDGET))

        cancelButton = qtw.QPushButton("Cancel", self.deleteDeliveredCancelWIDGET, clicked=lambda: self.cancelBillDELETEDELIVERCANCELF())
        cancelButton.setFixedSize(widgetPercentageValue(25, "w", self.deleteDeliveredCancelWIDGET), widgetPercentageValue(25, "h", self.deleteDeliveredCancelWIDGET))
        cancelButton.move(widgetPercentageValue(60, "w", self.deleteDeliveredCancelWIDGET), widgetPercentageValue(15, "h", self.deleteDeliveredCancelWIDGET))
        
        deleteButton = qtw.QPushButton("Delete", self.deleteDeliveredCancelWIDGET, clicked=lambda: self.deleteProductFromBillF(itemIndex))
        deleteButton.setFixedSize(widgetPercentageValue(30, "w", self.deleteDeliveredCancelWIDGET), widgetPercentageValue(25, "h", self.deleteDeliveredCancelWIDGET))
        deleteButton.move(widgetPercentageValue(35, "w", self.deleteDeliveredCancelWIDGET), widgetPercentageValue(55, "h", self.deleteDeliveredCancelWIDGET))
        deleteButton.setObjectName("deleteButton")


        self.deleteDeliveredCancelWIDGET.setStyleSheet("""
            #dodocWIDGET {
                border: 2px solid black;
                border-radius: 20%;
            }
            #deleteButton {
                background-color: red;
                color: white;
            }
            QPushButton:hover#deleteButton {
                background-color: #ff8c66;
            }
        """)

        self.deleteDeliveredCancelWIDGET.setWindowFlags(qtc.Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
        self.deleteDeliveredCancelWIDGET.show()


    # Delete | Delivered | Cancel functions;
    def ProductFromBillDeliveredF(self, itemIndex):
        # Sending the server the request about the product;
        self.sendServerBillItemDeliveredOrDeletedRequestF("deliver", itemIndex)
        self.DELETEDELIVEREDCANCELWIDGETEXISTS = False
        self.deleteDeliveredCancelWIDGET.deleteLater()
    

    def deleteProductFromBillF(self, itemIndex):
        self.sendServerBillItemDeliveredOrDeletedRequestF("del", itemIndex)
        self.DELETEDELIVEREDCANCELWIDGETEXISTS = False
        self.deleteDeliveredCancelWIDGET.deleteLater()


    def cancelBillDELETEDELIVERCANCELF(self):
        self.DELETEDELIVEREDCANCELWIDGETEXISTS = False
        self.deleteDeliveredCancelWIDGET.deleteLater()


    # The functon for sending the server a request about deleting or delivering a product;
    # Data is given by parameters;
    def sendServerBillItemDeliveredOrDeletedRequestF(self, editStyle, itemIndex):
        deliveredOrDeletedRES = req.post(f"{ServerUrl}editBillItemData", data={"restaurantID": GLOBALUSERDATA["restaurantID"], "password": GLOBALUSERDATA["password"], "curTabIndex": self.currentTableINDEX, "itemIndex":itemIndex, "editStyle": editStyle}).json()
        # Checking if the edit/delete was succesfull, if it was,
        # Checking the editStyle, if the edit style is deliver setting the itemindex backgroundcolor to orange and disabling its function to edit;
        # Otherwise, deleting the item from the scroller;
        print(itemIndex)
        if editStyle == "deliver":
            self.billProductButtons[itemIndex].setStyleSheet("background-color: #ff7f27; border: 1px solid black; border-radius: 10;")
            self.billProductButtons[itemIndex].setEnabled(False)
        else:
            self.setBillPageDataProperlyPostServerRequestF()
            

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        

    # The function for loading all the product categories from the json file;
    # This function only assigns the values to the self.CategoriesArr,
    # The rendering is done by another function;
    def loadProductCategoriesF(self):
        self.CategoriesArr = []
        # Loading the categories data from the json file;
        with open("./Data/Products/all_productKeeper.json") as pclnr:
            productCategoriesLoaderV = json.load(pclnr)
        # Adding the paths/values to the categories Arr;
        self.CategoriesArr = productCategoriesLoaderV["pPathList"]
        
            
    # So long as the required categories data is loaded, 
    # this function can be called to render all the categories to the scroller;
    def renderProductCategoriesF(self):
        x=0
        y=0
        categoryButtonStaticSize = (250, 125)
        maxYAXIS = int(self.prodOrCatScroller.width() // categoryButtonStaticSize[0])
        for category in self.CategoriesArr:
            if y >= maxYAXIS:
                x+=1
                y=0
            # Creating the category button;
            catBTN = qtw.QPushButton(category["prodCatName"], clicked=lambda ignore, btnPar=category["path"], btnName=category["prodCatName"]: self.viewCategoryProductsF(btnPar, btnName)) # [0:len(category)-5]
            catBTN.setFixedSize(categoryButtonStaticSize[0], categoryButtonStaticSize[1])
            catBTN.setStyleSheet("background-color: #7d6d92; border: 3px solid #c3c3c3; border-radius: 50%; color: white;")
            catBTN.setFont(qtg.QFont("Arial", adakPV(1.2, "w", app)))

            # Adding the category button to the self.allCategoriesButtons();
            self.allCategoriesButtons.append(catBTN)

            # Adding the category button to the self.prodOrCatGrid; 
            self.prodOrCatGrid.addWidget(catBTN, x, y)

            # Incrementing the y as usual;
            y+=1
        

    # This function clears all the array elements from self.allCategoriesButtons,
    # Resulting in the categories scroller being cleared;
    # NOTE: This only works for categories buttons, for removing products, please use: self.clearAllProductsFromScrollerF()
    def clearAllCategoriesFromScrollerF(self):
        for categoryButton in self.allCategoriesButtons:
            categoryButton.setParent(None)
        # Clearing the array now;
        self.allCategoriesButtons.clear()
    
    # Clearing the products;
    def clearAllProductsFromScrollerF(self):
        for productButton in self.allProductsButtons:
            productButton.setParent(None)
        # Clearing the array now;
        self.allProductsButtons.clear()

    
    # The function used for loading the products to the scroller;
    # This function does NOT render the data, it just loads it to an array;
    def loadProductsF(self, productPath):
        self.productsArr = []
        with open(productPath) as prodLoader:
            productData = json.load(prodLoader)["prodData"]
        # Loading the data to an array;
        self.productsArr = productData
        
    
    # This function renders all the loaded products;
    # The data is required to be loaded to be rendered, as this functions does't load the data;
    # Products loading is by: loadProductsF()
    def renderProductsF(self):
        # Creating the buttons now;
        x=0
        y=0
        productButtonStaticSize = (300, 100)
        maxYAXIS = int(self.prodOrCatScroller.width() // productButtonStaticSize[0])
        for product in self.productsArr:
            if y >= maxYAXIS:
                x+=1
                y=0
            # Creating the prduct button;
            productButton = qtw.QPushButton(f"{product['name']}\n{product['price']}€", clicked=lambda ignore, parData = (product['name'], product['price']):self.addItemToBillF(parData)) #clicked=lambda ignore:
            productButton.setFixedSize(productButtonStaticSize[0], productButtonStaticSize[1])
            
            productButton.setStyleSheet("background-color: #5b5b73; border: 2px solid #7d6d92; border-radius: 50%; color: white;")
            productButton.setFont(qtg.QFont("Arial", adakPV(1.2, "w", app)))

            # Adding the product button to the self.allProductsButtons;
            self.allProductsButtons.append(productButton)

            # Adding the product button to the self.prodOrCatGrid; 
            self.prodOrCatGrid.addWidget(productButton, x, y)

            # Incrementing the y as usual;
            y+=1

    
    # This function is called by the category buttons;
    # It's used to view/access the products in the desired category;
    # The method is, clearing the categories buttons and loading product data instead;
    # Setting the header label to the current category;
    # Disabling the goback button and creating a new button to leave the current category;
    # Once the button for leaving the current category is clicked, rerendering the categories,
    # Removing the leave category button and setting the header back to "categories";
    # Also clearing the products array to save memory;
    def viewCategoryProductsF(self, categoryPath, categoryName):
        # Firstly, clearing the categories buttons;
        self.clearAllCategoriesFromScrollerF()
        # Setting the header text to the current category name;
        self.catOrProdHeaderText.setText(categoryName)
        # Setting the gotocategories button's visibility to true;
        self.viewCategoriesButton.setVisible(True)
        # Loading the products;
        self.loadProductsF(categoryPath)
        # Rendering the products;
        self.renderProductsF()


    # This functions is used to view the categories after viewing products;
    # Based of the way this function deals with data, it's not suitable to run at start though once the initial start data is loaded, its a safe-to-call function;
    def viewCategoriesF(self):
        # Setting the "view categories" button's visibility to False;
        self.viewCategoriesButton.setVisible(False)
        # Setting the header text's value to "Categories";
        self.catOrProdHeaderText.setText("Categories")
        # Clearing the products;
        self.clearAllProductsFromScrollerF()
        # Loading the categories;
        self.loadProductCategoriesF()
        # Rendering the categories;
        self.renderProductCategoriesF()

    

    # This function is called from the products buttons, 
    # when it is clicked, the data from the products button is sent here via parameters;
    # Those parameters are then sent to the server for adding a new item to the bill, 
    # if the server accepts the authentication, the data is gonna be addedd to the bill;
    def addItemToBillF(self, billData):
        itemCount = self.getEntryOfItemCountF()
        if itemCount != 0:
            res = req.post(f"{ServerUrl}addItemToBill", data={
                                                                "rid": GLOBALUSERDATA["restaurantID"], 
                                                                "p": GLOBALUSERDATA["password"],
                                                                "cti": self.currentTableINDEX,
                                                                "itemd": [
                                                                    billData[0],
                                                                    billData[1],
                                                                    itemCount
                                                                ]
                                                            }).json()
            #res = req.post(f"{ServerUrl}addItemToBill", data={"aa": "wowwwwww"})
            print(res)


    # The function for getting the item count entry so the desired amount of a specific item can be added to the bill;
    # If the length of the entry is 0, which means there is no entry, we add a default value of the item to the bill, which is one;
    # If the entered value is not a number, we return a 0 as there is already a comparison to see if the return is 0, and if it is zero, nothing happens;
    # If the entred value is 0, it gets proccessed as a normal number but as there is the 0 comparison, nothing happens;
    # If the entered value is a float, it gets turned into an integer on return so it also works as a normal integer value;
    def getEntryOfItemCountF(self):
        itemCountEntry = self.newProductsCountEntry.text()
        if len(itemCountEntry) > 0:
            if is_number(itemCountEntry):
                self.newProductsCountEntry.setText("")
                return int(itemCountEntry)
            else:
                qtw.QMessageBox.critical(self, "Error", "Please enter a valid number as the item count;")
                return 0
        else:
            return 1

    def paidAmountEntryIsValid(self):
        paidAmountEntry = self.paidAmountEntry.text()
        if is_number(paidAmountEntry):
            return True
        else:
            return False

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # The function for selling the item;
    def tableTransactionF(self):
        # Checking if the client side values are proper;
        if self.validateTransactionClientsideF():
            # Getting the tables data from a request first, as on the transaction call it will be deleted if all goes right;
            # The value gotten now will be used for billing/stats;
            self.dataSoldInTransaction = req.post(f"{ServerUrl}singleTableData", data={"restaurantID": GLOBALUSERDATA["restaurantID"], "password": GLOBALUSERDATA["password"], "curTabIndex": self.currentTableINDEX}).json()
            
            # Clientside values are proper, sending the server a request now;
            transactionRequestF = req.post(f"{ServerUrl}doTransaction", data={"restaurantID": GLOBALUSERDATA["restaurantID"], "password": GLOBALUSERDATA["password"], "curTabIndex": self.currentTableINDEX}).json()



            # Checking if the transaction was succesfull;
            if transactionRequestF["validity"]:
                # Successfull;
                # Creating a current time instance;
                self.currentSaleCompleteTime = time.strftime('%m-%d-%Y-%H-%M-%S')
                self.currentSaleDayDate = time.strftime('%m-%d-%Y')
                self.currentSaleMonthDate = time.strftime('%m-%Y')

                # Setting some more values in the [self.dataSoldInTransaction] to be used in the Bill/App Stats;
                self.dataSoldInTransaction["SaleTime"] = self.currentSaleCompleteTime
                self.dataSoldInTransaction["totalWithTax"] = float(self.totalWithTVHSTEXTVALUE)
                self.dataSoldInTransaction["compName"] = "COMPANY NAME"
                self.dataSoldInTransaction["taxValue"] = "17%"

                # Clearing the bill data from the screen;
                self.clearBasicTransactionDataFromScreenF()
                # Saving the bill data;
                self.saveBillDataAsSaleF()
                # Printing the invoice;
                self.printBillInvoice()




            else:
                # Not succesfull;
                qtw.QMessageBox.information(self, "Info", transactionRequestF["msg"])


    # This function is called after succesfull transactions;
    # Saves the bill as a file and calls the "printBillInvoice" function;
    def saveBillDataAsSaleF(self):
        # Creating the complete time json file for using statistics and also setting the data properly based of the counts;
        with open(f"./Data/Sales/AllDoneBills/{str(self.currentSaleCompleteTime)}.json", "w") as billFileCompleteTimeFile:
            json.dump(fullTimeActualBillDataSorterF(self.dataSoldInTransaction), billFileCompleteTimeFile, indent=2)

        # Creating the txt file which will be the actual printed file;
        # Using io module as the normal python io operations for some reason dont display the euro sign on write, even though documentation says python uses utf-8;
        # So for that, using io module and specifying utf-8;
        billFileToPrint = io.open(f"./Data/Sales/printBills/{str(self.currentSaleCompleteTime)}.txt", mode="w", encoding="utf-8")
        # Fetching the data from the json file now and setting the data visually properly;
        with open(f"./Data/Sales/AllDoneBills/{str(self.currentSaleCompleteTime)}.json") as billFileJsonToRead:
            billData = json.load(billFileJsonToRead)
        
        # Creating the string which will be put into the file;
        billFileTEXT = ""

        # Writing the header data;
        billFileTEXT += f"               {billData['compName']}               "
        billFileTEXT += "\n\n\n\n\n"                                          #
        billFileTEXT += " |     PRODUCT     |   COUNT   |     PRICE     | \n\n"

        # Writing all the bill items;
        for singleBillItem in billData["tBill"]:
            billFileTEXT += f" |     {singleBillItem['n']}     |     {singleBillItem['c']}     |     {singleBillItem['p']}\u20AC    | \n"
        
        billFileTEXT += "\n\n\n\n"

        # Writng the footer data;
        billFileTEXT += f"Sale time: {billData['SaleTime']}\n"
        billFileTEXT += f"Total: {billData['tbp']}\n"
        billFileTEXT += f"Total with tax: {billData['totalWithTax']}\n"
        billFileTEXT += f"Tax value: {billData['taxValue']}"



        # Writing the billFileTEXT to the billFileToPrint;
        billFileToPrint.write(billFileTEXT)

        # Closing the bill file;
        billFileToPrint.close()

        # Writing to the monthly/daily total files;
        
        self.totalPriceTOWRITETOFILE = billData["tbp"]
        # Daily total file;
        self.checkIfDayFileExists()
        # Monthly total file;
        self.checkIfMonthFileExists()
        # Calling the print printBillInvoice function
        self.printBillInvoice()


    # This function prints the invoice of the transaction;
    def printBillInvoice(self):
        # C:\Users\Led-Com.CH\Desktop\Alcoft-Restaurant-Pos\AlcoftRestaurantV3-2021\ClientSide-Desktop\Data\Sales\printBills
        printFile = os.path.join("Data", "Sales", "printBills", str(self.currentSaleCompleteTime) + ".txt")
        print(printFile)
        #win32api.ShellExecute(0, "print", printFile, '/d:"%s"' % win32print.GetDefaultPrinter (),".",  0)
    


    # The functions for checking if monthly/daily files exist and if they dont creating them;
    # If the file exists, appending the price to the file, otherwise, creating the function and calling self;
    def checkIfDayFileExists(self):
        fileNameDAY = f"./Data/Sales/time_totals/daily/{str(self.currentSaleDayDate)}.txt"
        if os.path.isfile(fileNameDAY):
            # Reading the day total;
            dayTotalFILEREAD = open(fileNameDAY, "r")
            dayPastTotal = str(dayTotalFILEREAD.read())
            dayTotalFILEREAD.close()

            # Writing the day value;
            dayTotalFILEWRITE = open(fileNameDAY, "w")
            dayTotalFILEWRITE.write(str(float(dayPastTotal) + self.totalPriceTOWRITETOFILE))
            dayTotalFILEWRITE.close()

        else:
            with open(fileNameDAY, "w") as dayFile:
                dayFile.write(str(0))
            # Calling self;
            self.checkIfDayFileExists()


    def checkIfMonthFileExists(self):
        fileNameMONTH = f"./Data/Sales/time_totals/monthly/{str(self.currentSaleMonthDate)}.txt"
        if os.path.isfile(fileNameMONTH):
            # Reading the day total;
            monthTotalFILEREAD = open(fileNameMONTH, "r")
            monthPastTotal = str(monthTotalFILEREAD.read())
            monthTotalFILEREAD.close()

            # Writing the day value;
            monthTotalFILEWRITE = open(fileNameMONTH, "w")
            monthTotalFILEWRITE.write(str(float(monthPastTotal) + self.totalPriceTOWRITETOFILE))
            monthTotalFILEWRITE.close()

        else:
            with open(fileNameMONTH, "w") as monthFile:
                monthFile.write(str(0))
            # Calling self;
            self.checkIfMonthFileExists()


    # The function for clearing the bill price/tax values etc.. from the screen;
    def clearBasicTransactionDataFromScreenF(self):
        self.totalLabel.setText("")
        self.totalWithTVSH.setText("")
        self.viewPaidAmounttLabel.setText("")

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~



    # The function for checking if the values in the app are valid for proceeding to a transaction;
    def validateTransactionClientsideF(self):
        # Transaction clientside authentication;
        # Checking if the entered pay is a proper number;
        if self.paidAmountEntryIsValid():
            paidAmount = float(self.paidAmountEntry.text())
            # Checking if the paidAmount is larger than the required price;
            if paidAmount >= self.totalBillPrice:
                return True
            else:
                qtw.QMessageBox.critical(self, "Error", "The pay isn't sufficient;")
                return False
        else:
            qtw.QMessageBox.critical(self, "Error", "Please enter a valid number as the price entry;")
            return False



    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # The function for completely cancelling the transaction;
    # All the values are deleted from the server / the bill *completely* resets no matter the state of the delivery;
    def cancelTransactionFunctionDANGEROUSF(self):
        # Fetching the api for deleting the data and if the auth is completed the data's *will* be deleted;
        # IMPORTANT NOTE:
            # For now, the server will use the same function as the transaction function for clearing the data, 
            # but in the future I (we, hopefully :)) might change the called funciton on the server as I might need to to some server-side stats sometimes;
        # Firstly, asking the client if they "really" mean deleting the transaction;
        if not(self.DELETETRANSACTIONWIDGETEXSTS):
            self.DELETETRANSACTIONWIDGETEXSTS = True
            # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            self.confirmationWidget = qtw.QDialog()
            self.confirmationWidget.setFixedSize(250, 180)

            infoLabel = qtw.QLabel("Please enter 'CONFIRM'\n to delete the sale", self.confirmationWidget)
            infoLabel.setFont(qtg.QFont("Arial", 16))
            infoLabel.move(20, 16)

            confirmEntry = qtw.QLineEdit(self.confirmationWidget)
            confirmEntry.setPlaceholderText("CONFIRM")
            confirmEntry.setFixedSize(210, 26)
            confirmEntry.setFont(qtg.QFont("Arial", 16))
            confirmEntry.move(20, 64)

            def checkIfSaleCancellationConfirmed():
                if confirmEntry.text() == "CONFIRM":
                    self.confirmationWidget.deleteLater()

                    # Confirmed so actually deleting the sale;
                    self.actuallyDeleteSaleF()
                else:
                    qtw.QMessageBox.critical(self.confirmationWidget, "Error", "Please enter 'CONFIRM' with all capital letters if you want to cancel the sale")

            def deleteConfirmWidgetF():
                self.confirmationWidget.deleteLater()

            deleteButton = qtw.QPushButton("Delete", self.confirmationWidget, clicked=lambda: checkIfSaleCancellationConfirmed())
            deleteButton.setFixedSize(80, 30)
            deleteButton.move(85, 100)

            cancelButton = qtw.QPushButton("Cancel", self.confirmationWidget, clicked=lambda: deleteConfirmWidgetF())
            cancelButton.setFixedSize(80, 30)
            cancelButton.move(85, 136)

            # Setting some window flags and showing the dialog;
            self.confirmationWidget.setWindowFlags(qtc.Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
            self.confirmationWidget.show()

            # As the event loop is over, setting the "widget exists" to false;
            self.DELETETRANSACTIONWIDGETEXSTS = False

    # The function for actually deleting the transaction;
    # This is the function that will do the server request and deal with other stuff;
    def actuallyDeleteSaleF(self):
        # Sending the server request;
        deletionRequestRes = req.post(f"{ServerUrl}delSale", data={"restaurantID": GLOBALUSERDATA["restaurantID"], "password": GLOBALUSERDATA["password"], "curTabIndex": self.currentTableINDEX }).json()
        print(deletionRequestRes)
        # Checking if the deletion request is confirmed or not;
        if deletionRequestRes["validity"]:
            qtw.QMessageBox.information(self.confirmationWidget, "Info", "The sale has been cancelled.")
        else:
            qtw.QMessageBox.critical(self.confirmationWidget, "Error", "The sale has not been cancelled.")

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def goBackF(self):
        # Checking if the "delete edit cancel" widget exists, if it does, closing it as if it stays open a QT C/C++ Error is given and the app crashes;
        if self.DELETEDELIVEREDCANCELWIDGETEXISTS:
            self.deleteDeliveredCancelWIDGET.deleteLater()
        self.deleteLater()


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Standby Screen;
class StandbyScreen(qtw.QWidget):
    def __init__(self):
        super().__init__()
        

        # Setting the buttons styles;
        self.setStyleSheet("""
            QPushButton {
                border: 1px solid gray;
                border-radius: 20;
                background-color: white;
            }
            QPushButton:hover:!pressed {
                border: 1px solid lightgray;
                background-color: #aaa;
                color: #0f0c5c;
            }
        """)


        # Loading the settings to be used throughout the screen;
        with open("./Data/settings.json") as stl:
            sl = json.load(stl)
        SETTINGS = sl["standbySettings"]

        # Setting the background to the settings color;
        bgFrame = qtw.QFrame(self)
        bgFrame.setFixedSize(adakPV(100, "w", app), adakPV(100, "h", app))
        bgFrame.setStyleSheet(f"background-color: {SETTINGS['standbyBackgroundColor']};")
        bgFrame.move(0, 0)

        # Logo Image;
        logoImage = qtg.QPixmap(SETTINGS["standByLogo"])
        logoLabel = qtw.QLabel(self)
        logoLabel.setPixmap(logoImage)
        logoLabel.move(int((app.primaryScreen().size().width()/2)-(logoImage.width()/2)), int((app.primaryScreen().size().height()/2)-(logoImage.height()/2)))
        
        # Creating the shadow for the clock;
        shadow = qtw.QGraphicsDropShadowEffect()
        shadow.setBlurRadius(SETTINGS["standbyClockShadowRadius"])
        shadow.setColor(qtg.QColor(SETTINGS["standbyClockShadowColor"]))

        # Time Label;
        self.timeLabel = qtw.QLabel("                       ", self)
        self.timeLabel.setFont(qtg.QFont("Arial", adakPV(5, "w", app)))
        self.timeLabel.setGraphicsEffect(shadow)
        self.timeLabel.setStyleSheet(f"color: {SETTINGS['standbyClockTextColor']}")
        self.timeLabel.move(adakPV(37.9, "w", app), adakPV(85, "h", app))

        # MainPage Button;
        goToMainButton = qtw.QPushButton("Homepage", self, clicked=lambda: self.goToMainPage())
        goToMainButton.setFont(qtg.QFont("Arial", adakPV(2, "w", app)))
        goToMainButton.setFixedSize(adakPV(18, "w", app), adakPV(7, "h", app))
        goToMainButton.move(adakPV(81, "w", app), adakPV(80, "h", app))
        gtmpShadow = qtw.QGraphicsDropShadowEffect()
        gtmpShadow.setBlurRadius(SETTINGS["standbyButtonShadowRadius"])
        gtmpShadow.setColor(qtg.QColor(SETTINGS["standbyButtonShadowColor"]))
        goToMainButton.setGraphicsEffect(gtmpShadow)

        # Quit App Button;
        quitAppButton = qtw.QPushButton("Quit", self, clicked=lambda:sys.exit())
        quitAppButton.setFont(qtg.QFont("Arial", adakPV(2, "w", app)))
        quitAppButton.setFixedSize(adakPV(18, "w", app), adakPV(7, "h", app))
        quitAppButton.setStyleSheet("background-color: red; color: white;")
        quitAppButton.move(adakPV(81, "w", app), adakPV(90, "h", app))
        quitShadow = qtw.QGraphicsDropShadowEffect()
        quitShadow.setBlurRadius(SETTINGS["standbyButtonShadowRadius"])
        quitShadow.setColor(qtg.QColor(SETTINGS["standbyButtonShadowColor"]))
        quitAppButton.setGraphicsEffect(quitShadow)
        
        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        # My ad;
        # Label;
        myAdLabel = qtw.QLabel("Software by Alcoft", self)
        myAdLabel.setStyleSheet("color: white;")
        myAdLabel.setFont(qtg.QFont("Arial", adakPV(1.5, "w", app)))
        myAdLabel.move(adakPV(82, "w", app), adakPV(20, "h", app))
        # Logo:
        myLogo = qtg.QPixmap("./Data/Images/alcoft-logo-nobg.png")
        myLogoLabel = qtw.QLabel(self)
        myLogo.scaledToWidth(adakPV(12, "w", app))
        myLogo.scaledToHeight(adakPV(12, "h", app))
        myLogoLabel.setPixmap(myLogo)
        myLogoLabel.move(adakPV(84, "w", app), adakPV(1, "h", app))
        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

        # The timer;
        timer = QTimer(self)
        timer.timeout.connect(self.showTime)
        timer.start(1000) # Setting the one second delay for the timer;





        #
    # method called by timer
    def showTime(self):
        current_time = QTime.currentTime()
        label_time = current_time.toString('hh:mm:ss')
        self.timeLabel.setText(label_time)

    # Method for going to the mainpage
    def goToMainPage(self):
        appStack.setCurrentIndex(gotoMainWindowINDEX)



# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Take Aways Screen;
# This screen will show all the takeaway orders;
class TakeAwayWidget(qtw.QWidget):
    def __init__(self):
        super().__init__()


        # Showing the screen in FullScreen;
        self.setWindowFlags(qtc.Qt.WindowStaysOnTopHint)
        self.showFullScreen()



# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Browser Widget,
# The reason for using a widget instead of a stackedWidget is the fact that browser makes the app really laggy, 
# so running it on a different thread is a really good idea and prevents the lag completely;
class BrowserWidget(qtw.QWidget):
    def __init__(self):
        super().__init__()
        
        # WebSearch bar;
        self.searchBarEntry = qtw.QLineEdit(self)
        self.searchBarEntry.setFixedSize(adakPV(70, "w", app), adakPV(5, "h", app))
        self.searchBarEntry.setFont(qtg.QFont("Arial", adakPV(2, "w", app)))
        self.searchBarEntry.move(adakPV(10, "w", app), adakPV(2, "h", app))
        self.searchBarEntry.setStyleSheet("border: 1px solid black; border-radius: 25%;")

        # Search Button;
        self.searchButton = qtw.QPushButton("🔍", self, clicked=lambda:self.searchF())
        self.searchButton.setFont(qtg.QFont("Arial", adakPV(2, "h", app)))
        self.searchButton.setFixedSize(adakPV(6, "w", app), adakPV(5, "h", app))
        self.searchButton.move(adakPV(81, "w", app), adakPV(2, "h", app))

        # Browser Location;
        self.browser = qtWebEngineLOADER.QWebEngineView(self)
        self.browser.setUrl(qtc.QUrl("https://www.google.com"))
        self.browser.setFixedSize(adakPV(100, "w", app), adakPV(80, "h", app))
        self.browser.move(0, adakPV(8, "h", app))

        # Go Back Button;
        goBackButton = qtw.QPushButton("ᐊ Back", self, clicked=lambda:self.goBackF()) 
        goBackButton.setStyleSheet("background-color: red; color: white; border-radius: 50%")
        goBackButton.setFont(qtg.QFont("Arial", int(adakPV(1.9, "w", app)/1.5)))
        goBackButton.setFixedSize(adakPV(10, "w", app), adakPV(6, "h", app))
        goBackButton.move(adakPV(86, "w", app), adakPV(92, "h", app))
        

        # Showing fullscreen;
        self.showFullScreen()
    # Search Function
    def searchF(self):
        self.browser.setUrl(qtc.QUrl(f"http://{self.searchBarEntry.text()}"))

    # Function for going back to the main window;
    def goBackF(self):
        self.deleteLater()



#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# The function sending the request to the server, and returning the json;
# Parameters are the object of "restaurantID" and "password";
def sendLoginRequest(userData):
    return req.post(f"{ServerUrl}login", data=userData).json()
    # qtw.QMessageBox.critical("Network Error", "No internet connection, please connect to the internet to use the application.")
def LoginAuthTK():
	APW = tk.Tk()
	# the function for attempting to login;
	def attemptLogin():
		global GLOBALUSERDATA
		# Sending a request to the server and saving the response to a variable, if the request is accepted setting the variable to global data via a retur to the main;
		res = sendLoginRequest({"restaurantID": businessIdEntry.get(), "password": passEntry.get()})
		print(res)
		if res["validity"]:
			#GLOBALUSERDATA = res NOTE
			APW.destroy()
		else:
			messagebox.showerror("error", res)
	def checkIfAllEntriesAreValidF():
		if len(businessIdEntry.get()) > 0:
			if len(passEntry.get()) > 0:
				attemptLogin()
			else:
				messagebox.showerror("Error", "Please enter a password.")
		else:
			messagebox.showerror("Error", "Please enter a restaurant ID.")	
	top = str(int((APW.winfo_screenheight()/2)-150))
	side = str(int((APW.winfo_screenwidth()/2)-150))
	APW.geometry(f"300x300+{side}+{top}")
	APW.resizable(False, False)
	APW.title("Alcoft: Login")
    # Backgeround Image;
	loginImage = ImageTk.PhotoImage(Image.open("./Data/Images/loginWindowIMG.jpg"))
	tk.Label(APW, image=loginImage).pack()
    # Id Entry;
	businessIdEntry = tk.Entry(APW, bg="#515151", font=("Arial", 16), fg="white")
	businessIdEntry.place(x=30,y=135)
	# Password Entry;
	passEntry = tk.Entry(APW, bg="#515151", font=("Arial", 16), fg="white", show="*")
	passEntry.place(x=30,y=195)
	# Login Button;
	loginBtn = tk.Button(APW, text="Login", bg="#aaa", font=("Courier", 15), padx=10, command=lambda:checkIfAllEntriesAreValidF())
	loginBtn.place(x=105, y=240)
    # Binding the enter key to the login button;
	APW.bind('<Return>', lambda event=None: loginBtn.invoke())
	APW.mainloop()
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~



# Starting the app if only its called by itself;
if __name__ == "__main__":
    #LoginAuthTK() # App cant continue before the mainloop is killed; #NOTE
    # As the login is successfull, starting the mainapp now;
    app = qtw.QApplication(sys.argv)      # creating the app instance;

    GLOBALUSERDATA = {"restaurantID": "elegant", "password": "123", "userData": {"tableCount": 3, "tableFillStates": [True, False, True]}} #NOTE

    # Creating the appstack;
    appStack = qtw.QStackedWidget()

    # Creating from the standby screen
    _standbyScreen = StandbyScreen()
    appStack.addWidget(_standbyScreen)
    
    # The screens for settings/statistics/browser/Products;
    appStack.addWidget(MainWindow())
    appStack.addWidget(SettingsScreen())
    appStack.addWidget(StatisticsScreen())
    appStack.addWidget(ProductsScreen())

    # The indexes of the screens;
    goToStandbyINDEX     = 0
    gotoMainWindowINDEX  = 1
    gotoSettingsINDEX    = 2
    gotoStatisticsINDEX  = 3
    gotoProductsINDEX    = 4

    # Showing the appStack;
    appStack.showFullScreen()

    #NOTE
    appStack.setCurrentIndex(gotoStatisticsINDEX)
    
    app.exec_()                           # executing the app;
    sys.exit()                            # Clearing the exits with a system exit call; 


