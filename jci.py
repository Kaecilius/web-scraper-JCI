import requests
from bs4 import BeautifulSoup
import pandas as pd
import json
import datetime

def getCredentials(file, prod, type):
    fileObject = open(file, "r")
    jsonContent = fileObject.read()
    data = json.loads(jsonContent)
    filter_data = list( filter( (lambda x: x["prod"] == prod and x["type"] == type), data) )[0]
    return filter_data

def getLoginSessionJCI():
    data = getCredentials("credentials.json", 1, "JCI")
    login_url = data["loginurl"]
    username = data["username"]
    password = data["password"]
    payload = {"username":username,"password":password, "login":"LOGIN"}
    response = requests.post( login_url, data = payload)
    return response.cookies.get_dict()

def getFishmealPrice(date, cookies):
    # Date Format = 2023-8-15
    # China Domestic Super Prime Fishmeal Prices Daily Report (in RMB/MT)
    report_url = f"https://www.jcichina.com/pro/news_jgrb.aspx?re_date={date}&info_no=893562A&pro_name=%E8%B6%85%E7%BA%A7%E8%92%B8%E6%B0%94%E9%B1%BC%E7%B2%89&zw=JCI"
    response = requests.get( report_url, cookies = cookies)
    return response.text

def getTablePrices(html, date):
    soup = BeautifulSoup(html, "html.parser")
    table = str(soup.find("table"))
    df_prices = pd.read_html(table, skiprows=1, header=0)[0]
    df_prices["date"] = date
    return df_prices

dates = list( pd.date_range(start="2023-01-01", end=datetime.date.today()).astype(str) )
cookies = getLoginSessionJCI()

dfs = ( getTablePrices(getFishmealPrice(date, cookies), date) for date in dates)
df = pd.concat( dfs, ignore_index = True)
df.to_csv("expot_jci.csv", index= False)
print(df)