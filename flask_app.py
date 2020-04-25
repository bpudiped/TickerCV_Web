from flask import render_template
from flask import request
from flask import Flask

import sqlite3
import matplotlib
matplotlib.use("Agg")
#import numpy as np
import pandas as pd
import datetime
from datetime import date
import Ticker
import CV_Stats
import Plot
import Correlation
import HeatMap
import RSI
import SQL_Database as sqd
import sql_feedback as sfb

app = Flask(__name__)

#Creating and Initializing DB before ticker is entered
#ticker_file = '/home/bpudiped/mysite/tickercv.db'
ticker_file = ':memory:' # in-memory
#db = sqd.startDB(ticker_file)
db = sqlite3.connect(ticker_file)
cursor = sqd.createDB(db)
defaultTS = 'SPY'
defaultDate = datetime.date.today()-datetime.timedelta(days=30)
sqd.updateDB(db, defaultTS, 2, 3, defaultDate)

#fb_file = '/home/bpudiped/mysite/feedback.db' # in-memory
fb_file = ':memory:' # in-memory
# CREATE a database in RAM or file
fdb = sqlite3.connect(fb_file)
cursor = sfb.createfb_db(fdb)

def latestScores(start_date, end_date, tickerSymbol):

    debug = 0
    if debug == 1:
        print("start_date, end_Date, tickersymbol")
        print(start_date)
        print(end_date)
        print(tickerSymbol)

    url = "https://raw.githubusercontent.com/datasets/covid-19/master/data/time-series-19-covid-combined.csv"
    filename = url
    df = pd.read_csv(filename, lineterminator='\n')
    tdate = start_date

    sDates, sCloses = Ticker.Ticker(start_date, end_date, tickerSymbol)

    # Check if Ticker is Valid and if not use default tickersymbol
    validTicker = True
    if len(sDates) < 1:
        validTicker = False
        sDates, sCloses = Ticker.Ticker(start_date, end_date, defaultTS)


    scDates, tCases, scCloses = CV_Stats.CV_Stats(tdate, sDates, sCloses, df, end_date)
    sDates = scDates
    sCloses = scCloses
    sDates1 = pd.to_datetime(sDates)
    sDates1 = sDates1.strftime("%m-%d")
    score = Correlation.Correlate(sCloses, tCases)

    if debug == 1:
        print("sDates")
        print(sDates)

    score1 = RSI.computeRSI(sCloses, sDates, 10, 30)
    return score, score1, validTicker, sDates1, sCloses, tCases

@app.route('/')

def index():
    end_date = str(datetime.date.today())
    start_date1 = pd.to_datetime(end_date)
    start_date = start_date1 - datetime.timedelta(days=70)
    tdate = str(start_date.strftime("%Y-%m-%d"))

    cursor = db.cursor()
    all_rows = sqd.getAllDB(cursor)
    print("All_rows")
    print(all_rows)

    row0 = sqd.getRow0DB(cursor)
    #print(row0)
    if row0[3] < end_date:
        all_rows = sqd.getAllDB(cursor)
        for row in all_rows:
            score, score1, validTicker, sDates1, sCloses, tCases = latestScores(start_date, end_date, row[0])
            sqd.updateDB(db, row[0], score, score1, end_date)

    query = 'tickersymbol'

      # Ticker Symbol Entered
    if query in request.args:
        inputTS = request.args[query].upper()
    else:
        inputTS = defaultTS

    tickerSymbol = inputTS
    score, score1, validTicker, sDates1, sCloses, tCases = latestScores(tdate, end_date, tickerSymbol)

    if validTicker == False:
        tickerSymbol = defaultTS

    corrrow = sqd.getMaxDBCorr(cursor)
    rsirow = sqd.getMaxDBrsi(cursor)
    print("RSIrow")
    print(rsirow)
    sqd.updateDB(db, tickerSymbol, score, score1, end_date)

    plot_url = Plot.Plot(sDates1, sCloses, tickerSymbol, tCases)
    cmap2 = matplotlib.cm.spring
    plot_url1 = HeatMap.HeatMap(score, tickerSymbol, cmap2, corrrow[1], corrrow[0], -100, 100)

    cmap = matplotlib.cm.GnBu
    plot_url2 = HeatMap.HeatMap(score1, tickerSymbol, cmap, rsirow[2], rsirow[0], 0, 100)


    return render_template('index.html', title=('%s vs COVID-19' % tickerSymbol),
        validTicker=validTicker, plot_url1=plot_url1, plot_url2=plot_url2, plot_url=plot_url, symbol=inputTS)

#@app.route('/about')


@app.route('/feedback', methods = ['GET', 'POST'])
def feedback():

    if request.method == 'POST':
        uname = request.form.get('name1')
        ucomment = request.form.get('comment1')
        udate = date.today().strftime('%Y-%m-%d')
        sfb.updatefb_db(fdb, uname, ucomment, udate)
        return render_template('showfb.html', uname=uname, ucomment=ucomment)

    cursor = fdb.cursor()

    all_rows = sfb.getrecentfb_db(cursor, 5)
    return render_template('feedback.html', all_rows=all_rows)


