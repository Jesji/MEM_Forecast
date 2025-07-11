# webscraping script
from selenium import webdriver
from selenium.webdriver.common.by import By
from pathlib import Path
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os
import ast
import pandas as pd
import numpy as np
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import shutil


# url of generation data with the html code identifier for the date selection and download button
gen_url = r"https://www.cenace.gob.mx/Paginas/SIM/Reportes/EnergiaGeneradaTipoTec.aspx"

date_textbox_xpath = r'//*[@id="ctl00_ContentPlaceHolder1_Fecha{Inicial_Final}_dateInput"]'

download_button_xpath = r'//*[@id="ContentPlaceHolder1_DescargarReportes"]'


date_range_xpath = r'//*[@id="ctl00_ContentPlaceHolder1_FechaInicial_AD"]'



def create_download_folder():
    # download folder name
    download_folder = Path.cwd()/"Downloaded_data"
    if download_folder.exists():
        shutil.rmtree(download_folder)
    download_folder.mkdir(parents=True, exist_ok=True)
    return download_folder

# function to fill boxes
def textbox_fill(driver, xpath, date_string, attribute):
    # wait until the element is present
    textbox = WebDriverWait(driver, 2).until(EC.presence_of_element_located((By.XPATH, xpath))) 
    # write the date string to textbox
    textbox.send_keys(date_string) 
    time.sleep(1)
    # click tab to get out of textbox
    textbox.send_keys(Keys.TAB) 
    #time.sleep(1)
    # return the attribute of textbox
    return textbox.get_attribute(attribute)

# function to blank boxes 
def clear_textbox(driver,xpath):
    textbox = WebDriverWait(driver, 2).until(EC.presence_of_element_located((By.XPATH, xpath))) 
    #time.sleep(1)
    # clears textbox
    textbox.clear()

# funtion that turns timestamp format to 'mes de año' format
def time_to_string(date):
    meses = {
    1: "enero", 2: "febrero", 3: "marzo", 4: "abril",
    5: "mayo", 6: "junio", 7: "julio", 8: "agosto",
    9: "septiembre", 10: "octubre", 11: "noviembre", 12: "diciembre"}
    mes = date.month
    year = date.year
    return f"{meses[mes]} de {year}"

# function to download from an interval[0] to interval[1]
def donwload_interval(interval,driver):
    # start clearing the boxes
    clear_textbox(driver=driver, xpath=date_textbox_xpath.format(Inicial_Final='Inicial'))
    clear_textbox(driver=driver, xpath=date_textbox_xpath.format(Inicial_Final='Final'))
    # insert beginning date
    first_date = textbox_fill(
        driver=driver,
        xpath=date_textbox_xpath.format(Inicial_Final='Inicial'),
        date_string=interval[0],
        attribute='value'
    )
    # insert end date
    second_date = textbox_fill(
        driver=driver,
        xpath=date_textbox_xpath.format(Inicial_Final='Final'),
        date_string=interval[1],
        attribute='value'
    )
    # wait for download botton to be clickable
    download_button = WebDriverWait(driver, 2).until(EC.element_to_be_clickable((By.XPATH, download_button_xpath)))
    # click download button
    download_button.click()
    time.sleep(1)  
    try:
        # accepts download dialog
        WebDriverWait(driver, 2).until(EC.alert_is_present())
        driver.switch_to.alert.accept()
    except:
        pass
                  
    print("[✔] Botón de descarga clickeado.")
    print(f"Intervalo: {interval[0]} to {interval[1]} .\n")

# downloading specific date range
def selenium_download(beginning_date, end_date,download_folder):
    #download_folder = create_download_folder()
    chrome_options = Options()
    prefs = {
         #since donwload folder is a path object, has to be turned to string
         "download.default_directory": str(download_folder),
         "download.prompt_for_download":False,
         "donwload.directory_updgrade":False,
         "safebrowsing.enabled":True,
         "profile.default_content_settings.popups":0,
         "profile.default_content_settings_values.automatic_downloads":1
    }
    chrome_options.add_experimental_option("prefs",prefs)

    driver = webdriver.Chrome(options=chrome_options)

    driver.get(gen_url)

    # Get value of max and min date available in database
    value_str = WebDriverWait(driver, 2).until(
        EC.presence_of_element_located((By.XPATH, date_range_xpath))
    ).get_attribute("value")

    # Create interval of max and min dates
    dates_list = ast.literal_eval(value_str)
    whole_period = [pd.Timestamp(year=y, month=m, day=d) for y,m,d in dates_list]

    print(f"Date interval goes from {beginning_date} to {end_date}")
    #interval = [time_to_string(beginning_date), time_to_string(end_date)]

    # ranges by year to download whole period
    ys_range = pd.date_range(start=pd.Timestamp(beginning_date,1,1), end = pd.Timestamp(end_date,12,31), freq="YS")
    ye_range = pd.date_range(start=pd.Timestamp(beginning_date,1,1), end = pd.Timestamp(end_date,12,31), freq="YE")
    date_ranges = [[time_to_string(e),time_to_string(b)] for e,b in zip(ys_range,ye_range)]

    for interval in date_ranges:
        donwload_interval(interval,driver=driver)

    #donwload_interval(interval, driver=driver)
    driver.quit()


    