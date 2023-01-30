import datetime
import pandas as pd
import undetected_chromedriver as uc
from csv import writer
from time import sleep
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait




def append_list_as_row(file_name, list_of_elem):
    '''function to add a rox to a csv file'''
    # Open file in append mode
    with open(file_name, 'a', newline='') as write_obj:
        # Create a writer object from csv module
        csv_writer = writer(write_obj)
        # Add contents of list as last row in the csv file
        csv_writer.writerow(list_of_elem)

def get_vessel_position():
    '''Parse a list of vessels to get their positions'''
    # list of vessels given by Bloom
    vessels_source = '/root/Bloom_scrap/chalutiers_pelagiques.xlsx'
    # Class Name of privacy policy agreement button (might change)
    privacy_click = 'css-47sehv'  
    # get crawling timestamps
    crawling_timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
    # read the excel file to retreive IMO list
    df = pd.read_excel(vessels_source)
    vessel_list = df["IMO"].tolist() 
    # Connect to Marine Traffic with items of the list
    print("Start scrapping")
    for vessel in vessel_list:
        print(vessel)
        url= "https://www.marinetraffic.com/en/data/?asset_type=vessels&columns=shipname,imo,time_of_latest_position,lat_of_latest_position,lon_of_latest_position,status,speed,navigational_status&quicksearch|begins|quicksearch="+str(vessel)
        options = uc.ChromeOptions()
        options.add_argument("--disable-extensions")
        options.add_argument('--disable-application-cache')
        options.add_argument('--disable-gpu')
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-setuid-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--headless")
        driver = uc.Chrome(options=options, version_main=109)
        driver.get(url) 
        sleep(5) # wait for the page to load

        # if the IMO leads to  an answer then add it to the csv else add nan values
        try:
            WebDriverWait(driver, 5).until(lambda d: d.find_element(By.CLASS_NAME, "ag-body"))
            record = driver.find_element(By.CLASS_NAME, "ag-body")
            append_list_as_row('/root/bloom_scrap.csv',[crawling_timestamp]+record.text.split('\n'))
        except:
            append_list_as_row('/root/bloom_scrap.csv',[crawling_timestamp]+["nan",vessel,"nan","nan","nan"])
        
    driver.close()

get_vessel_position()

