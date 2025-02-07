import sqlite3
from sqlite3 import Error

import datetime
from datetime import date, timedelta

def startDB(database):
    # CREATE a database in file or RAM
    db = sqlite3.connect(database)
    return db

# Get a cursor object
def createDB(db):
    cursor = db.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS stocks(id INTEGER PRIMARY KEY, name TEXT UNIQUE, corrscore FLOAT, rsiscore FLOAT, udate DATE)''')
    db.commit()
    return cursor

# INITIALLIZE DB (called stocks) with 2 entries
def updateDB(db, name, corrscore, rsiscore, udate):
    cursor = db.cursor()
    cursor.execute('''INSERT or REPLACE INTO stocks(name, corrscore, rsiscore, udate) VALUES(?,?,?,?)''', (name, corrscore, rsiscore, udate))
    db.commit()
    return cursor

def updateToLatestDate(db):
    cursor = db.cursor()
    sdate = '2020-01-01'
    edate = datetime.strftime(datetime.now() - timedelta(1), '%Y-%m-%d')
    all_rows = getPriorDB(cursor, sdate, edate)
    for row in all_rows:
        ticker = row[1]
        # fix this score to latest ticker
        corrscore = '20'
        rsiscore = '20'
        today = datetime.strftime(datetime.now(), '%Y-%m-%d')
        updateDB(db, ticker, corrscore, rsiscore, today)

def getRow0DB(cursor):
    cursor.execute('''SELECT name, corrscore, rsiscore, udate FROM stocks''')
    row = cursor.fetchone()
    return row

    #SEARCH for MAX
def getAllDB(cursor):
    cursor.execute('''SELECT name, corrscore, rsiscore, udate FROM stocks''')
    all_rows = cursor.fetchall()
    return all_rows
    # for row in all_rows:
    # row[0] returns the first column in the query (name), row[1] returns 2nd column (score)
    #     return print('{0} : {1}'.format(row[0], row[1]))

# UPDATE stock with new MAX score
def getMaxDBCorr(cursor):
    cursor.execute('''SELECT name, max(corrscore), rsiscore, udate FROM stocks''')
    row = cursor.fetchone()
    return row

def getMaxDBrsi(cursor):
    cursor.execute('''SELECT name, corrscore, max(rsiscore), udate FROM stocks''')
    row = cursor.fetchone()
    return row

def getMinDBCorr(cursor):
    cursor.execute('''SELECT name, min(corrscore), rsiscore, udate FROM stocks''')
    row = cursor.fetchone()
    return row

def getMinDBrsi(cursor):
    cursor.execute('''SELECT name, corrscore, min(rsiscore), udate FROM stocks''')
    row = cursor.fetchone()
    return row

def getPriorDB(cursor, sdate, edate):
    cursor.execute('''SELECT * FROM stocks WHERE
    strftime('%s', udate) BETWEEN strftime('%s', ?) AND strftime('%s', ?)''', (sdate, edate))
    all_rows = cursor.fetchall()
    return all_rows


