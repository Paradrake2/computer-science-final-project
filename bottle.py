import sqlite3
from bottle import default_app, route, post, get, template, request, jinja2_view
import yfinance as yf
import numpy as np
import pandas as pd

db = sqlite3.connect("/home/leogold/mysite/views/sminfo.db")
c = db.cursor()

goback = """
    <form action = "/stockmarket" method ="get">
        <input type = "submit" value = "Go back to stock market page">
    </form>
"""

@route('/')
def hello_world():
    return template("index.html")
@route('/test')
def basicForm():
    l = ['AAPL', 'MMM']

    df_list = []

    for t in l:
        df_list.append(pd.DataFrame([yf.Ticker(t).history]))

    df = pd.concat(df_list)
    result = df.to_html()
    return template("test.html", result = result)
    #return 'asfjaskfnakfs'
@route('/index')
def index():
    return template("index.html")
@route('/bmi')
def bmi():
    return template("bmi.html")
@post('/convert')
def convert():
    height = request.forms.get("height")
    height = int(height)
    weight = request.forms.get("weight")
    weight = int(weight)

    bmi = (weight /  (height * height)) * 703
    bmi = float(bmi)

    if bmi >= 30:
        status = "Obese"
    elif bmi >= 25 and bmi < 30:
        status = "Overweight"
    elif bmi >= 18.5 and bmi < 25:
        status = "Normal"
    elif bmi < 18.5:
        status = "Underweight"

    return template("convert.html",bmi = bmi, status = status)
@route('/stockmarket')
def stockmarket():
    return template("stockmarket.html")
@post('/stockmarketinfo')
def stockmarketinfo():
    try:
        return template("stockmarketinfo.html")
    except:
        return template("error.html")
@post('/addtodatabase')
def addtodatabase():
    return template("addtodatabase.html", db = db, c = c)
@post('/database')
def database():
    return template("database.html", db = db, c = c)
@post('/cleardatabase')
def clearDatabase():
    sql = """
    DROP TABLE IF EXISTS stockinfo;
    CREATE TABLE stockinfo (
    id INTEGER PRIMARY KEY,
    name VARCHAR(20),
    marketPrice VARCHAR(20),
    previousClosePrice VARCHAR(20),
    dateTime VARCHAR(20)
    );
    """
    c.executescript(sql)
    return template("database.html", c = c)
@post('/deletestock')
def deleterecord():
    return template("deletestock.html", c = c, db = db)
@post('/deletestockconfirm')
def deleterecordcofirm():
    return template("deletestockconfirm.html", c = c, db = db)
@post('/deletestockresult')
def deletestockresult():
    return template("deletestockresult.html", c = c, db = db)
@post('/deletedstock')
def deletedstock():
    return template("deletestock.html", c = c, db = db)
@post('/history')
#@jinja2_view('history.html')
def history():
    return template("history.html")
@post('/historyresult')
def historyresult():
    try:
        stockChosen = request.forms.get("stock")
        start_date = request.forms.get("startdate")
        end_date = request.forms.get("enddate")
        data = yf.download(stockChosen, start = start_date, end = end_date)

        column = data["Open"]
        df = pd.DataFrame(column)
        open1 = df.iloc[0]
        #Uses negative indexing to find the last row in the dataframe
        open2 = df.iloc[-1]
        opencalc = open2 - open1

        column2 = data["Close"]
        df2 = pd.DataFrame(column2)
        close1 = df2.iloc[0]
        close2 = df2.iloc[-1]
        closecalc = close2 - close1

        column3 = data["Volume"]
        df3 = pd.DataFrame(column3)
        volume1 = df3.iloc[0]
        volume2 = df3.iloc[-1]
        volumecalc = volume2 - volume1

        column4 = data["High"]
        df4 = pd.DataFrame(column4)
        high1 = df4.iloc[0]
        high2 = df4.iloc[-1]
        highcalc = high2 - high1

        column5 = data["Low"]
        df5 = pd.DataFrame(column5)
        low1 = df5.iloc[0]
        low2 = df5.iloc[-1]
        lowcalc = low2 - low1

        opencalc = str(opencalc)
        opencal = opencalc.strip('dtype: float64')
        opencal = opencal.strip('Open ')

        closecalc = str(closecalc)
        closecal = closecalc.strip('dtype: float64')
        closecal = closecal.strip('Close ')

        volumecalc = str(volumecalc)
        volumecal = volumecalc.strip('dtype: int64')
        volumecal = volumecal.strip('Volume ')

        highcalc = str(highcalc)
        highcal = highcalc.strip('dtype: float64')
        highcal = highcal.strip('High ')

        lowcalc = str(lowcalc)
        lowcal = lowcalc.strip('dtype: float64')
        lowcal = lowcal.strip('Low ')

        result = data.to_html()

        return template("historyresult.html", result = result, opencalc = opencal, closecalc = closecal, volumecalc = volumecal, highcalc = highcal, lowcalc = lowcal)
    except:
        return template("error.html")
@post('/stockbuyer')
def stockbuyer():
    stockChoice = request.forms.get("stock")
    stock1 = yf.Ticker(stockChoice)
    data = stock1.recommendations.tail(10)
    result = data.to_html()
    grade = data['To Grade']
    grade = str(grade)

    overweight = grade.count("Overweight")
    buy = grade.count("Buy")
    sell = grade.count("Sell")
    outperform = grade.count("Outperform")
    underweight = grade.count("Underweight")
    neutral = grade.count("Neutral")
    #the most complicated stock analysis program ever to exist
    total = int(overweight) + int(buy) - int(sell) + int(outperform) - int(underweight)

    stance = ""

    if total > 5:
        to_buy = "yes"
    else:
        to_buy = "no"
    if neutral > 4:
        stance = "This stock has been rated as \"Neutral\". What this means is that either analysts expect the stock to perform in line with the market or the stock is starting to go downhill. Look at the \"From Grade\" section. If there are a lot of positives like buy, positive, etc, and in the adjacent \"To Grade\" section there is either neutral or some negative rating, that means that analysts are expecting the stock to go downhill and it would not be a good idea to buy it. "
    else:
        pass
    return template("stockbuyer.html", result = result, data = data, to_buy = to_buy, grade = grade, stance = stance)

application = default_app()
