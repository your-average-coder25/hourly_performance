
# Pip if selenium or webdriver_manager is not installed already
from selenium import webdriver
#https://pypi.org/project/webdriver-manager/
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
#https://selenium-python.readthedocs.io/locating-elements.html
from selenium.webdriver.common.by import By
import time
#https://pypi.org/project/print-color/
from print_color import print

#https://pypi.org/project/pandas/
import pandas

import os
from dotenv import load_dotenv
from pathlib import Path
import re
import numpy as np
import datetime

#variables that are hidden so they aren't accidentally pushed into github
#variables are all called using os.environ[variableName]
dotenv_path = Path('local.env')
load_dotenv(dotenv_path=dotenv_path)

#File path to where your chromedrive is located. Should be in the same directory as your project
PATH = os.environ["CHROMEDRIVER_PATH"]

#Had to add the handling in the next three lines because the chrome service stopped working the previous way it was done
chrome_install = ChromeDriverManager().install()
folder = os.path.dirname(chrome_install)
chromedriver_path = os.path.join(folder, PATH)

options = webdriver.ChromeOptions()
#Mainly used to reduce some messages on command line so it isn't as cluttered
options.add_argument('--ignore-certificate-errors')
options.add_argument('--ignore-ssl-errors')
options.add_argument("--disable-proxy-certificate-handler")
#driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()),options=options)
driver = webdriver.Chrome(service=ChromeService(chromedriver_path),options=options)

lightspeedLoginURL = "https://manager.lsk.lightspeed.app/"
driver.get(lightspeedLoginURL)

usernameTextBox = driver.find_element(By.XPATH,'//*[@id="username"]')

pwTextBox = driver.find_element(By.XPATH,'//*[@id="password"]')

loginButton = driver.find_element(By.XPATH,'//*[@id="login"]/div[3]/button')


usernameTextBox.send_keys(os.environ["LIGHTSPEED_USERNAME"])
pwTextBox.send_keys(os.environ["LIGHTSPEED_PASSWORD"])
loginButton.click()
#YYYY-MM-DD
startDate="2024-07-08"
endDate="2024-07-14"

dateFormat = "%Y-%m-%d"
startDateTime = datetime.datetime.strptime(startDate, dateFormat).date()
endDateTime = datetime.datetime.strptime(endDate, dateFormat).date()
week = 7 
d1 = startDateTime
datePairs = []
# Getting date range into Monday to Sunday pairs
# The heatmap starts on monday and ends on Sunday so ideally the date range starts on a monday and ends on a sunday
# Otherwise the pairs will not be correct
while d1 < endDateTime:
    datePairs.append((d1, d1 + datetime.timedelta(week-1)))
    d1 += datetime.timedelta(week)

print("Pairs Calculated")


headerRow = ("Date", "Day", "05:30", "06:00", "06:30", "07:00", "07:30", "08:00", "08:30", "09:00", "09:30", "10:00", "10:30", "11:00", "11:30", "12:00", "12:30", "13:00", "13:30", "14:00", "14:30", 
            "15:00", "15:30", "16:00", "16:30", "17:00", "17:30", "18:00", "18:30", "19:00", "19:30", "20:00", "20:30", "21:00", "21:30", "22:00", "22:30", "23:00", "23:30", 
            "00:00", "00:30", "01:00", "01:30", "02:00", "02:30", "03:00", "03:30", "04:00", "04:30", "05:00")
print(len(headerRow))
csvFile = pandas.DataFrame(data=None,columns=headerRow)

for startOfWeek,endOfWeek in datePairs:

    print("Start Date: " + startOfWeek.strftime(dateFormat))
    print("End Date: " + endOfWeek.strftime(dateFormat))
    driver.get(f"https://manager.lsk.lightspeed.app/reporting/heatmap/week/{startOfWeek.strftime('%Y-%m-%d')}/{endOfWeek.strftime('%Y-%m-%d')}")
    heatmapID = "heatmap"
    time.sleep(3)
    print("Heatmap Loaded")

    #Its not really a table but its presented like a table
    table = driver.find_element(By.ID, heatmapID)
    #data is just one large array
    data = table.find_elements(By.XPATH, ".//div")
    print("Retreived performance")
    print(len(data))

    #Reshaped into rows where each row is a separate day
    rows = np.reshape(data[0:len(data)-1],(8,49))

    currentDay = startOfWeek
    #Retrieving the days hourly performance and inserting into dataframe
    for row in rows[1:]:
        rowData = [None] * len(row)
        #rowData[0] = currentDay.strftime('%Y-%m-%d')
        rowData[0] = row[0].text
        for col in range(1, len(row)):
            rowData[col] = row[col].get_attribute("data-original-title")
            if rowData[col] is None:
                rowData[col] = "$0"
        rowData.insert(0,currentDay.strftime('%Y-%m-%d'))
        currentDay += datetime.timedelta(1)
        csvFile.loc[len(csvFile)] = rowData
        

csvFile.to_csv('hourly_performance_' + startDate + '_to_' + endDate + '.csv', sep=',')

#Waits for user to close command line window so it doesn't close on its own and you can review the current state of the browser
wait = input("Wait for input")  
   