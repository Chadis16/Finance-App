from flask import render_template, Flask, request, url_for, flash, redirect, session
from Investment_Transactions import investment_transactions
import plotly.express as px
import plotly.graph_objects as go
import mysql.connector
import yfinance as yf
import pandas as pd
import datetime
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta
import yfinance as yf
import csv
import numpy as np
from sqlalchemy import create_engine, insert, MetaData, Table, Column, Integer, String, DATE, FLOAT, text
from argon2 import PasswordHasher
import logging
import calendar


logging.basicConfig(filename='flask_debug.log', level=logging.DEBUG)

metadata = MetaData()

app = Flask(__name__)

app.secret_key = 'BAD_SECRET_KEY'

def login(username,password):
    engine = create_engine("mysql+mysqlconnector://root:Printhelloworld1!@127.0.0.1/users", echo=True)
    users = engine.connect()
    ph = PasswordHasher()
    if username == None:
        return 'Fail'
    else:
        res = ph.hash(password)
        test = pd.read_sql('SELECT * FROM users.users;',users)
        test = test[test['Username']==session['username']]
        test = test.iat[0,2]
        try:
            ph.verify(test, password)
            users.close()
            return "Pass"
        except Exception:
            print('Fail')
            return "Fail"

def trans(x,y,table):
    transactions = table
    transactions = transactions[transactions['idtransactions']==x]
    if y == 'Date':
        transactions = transactions.iat[0,1]
    elif y == 'Transaction':
        transactions = transactions.iat[0,2]
    elif y == 'Amount':
        transactions = transactions.iat[0,3]
    elif y == 'Category':
        transactions = transactions.iat[0,4]
    elif y == 'Account':
        transactions = transactions.iat[0,5]
    return transactions

@app.route('/', methods=['POST','GET'])
def signin():
    session['username'] = request.form.get('User')
    username = session['username']
    if username != None:
        username = username.lower()
        password = request.form.get('Password')
        Ok = login(username,password)
        if Ok == 'Pass':
            return redirect(url_for('BalanceTracking'))
        elif Ok == 'Fail':
            return render_template('LoginFail.html')
    else:
        return render_template('Login.html')

@app.route('/Register',methods=['POST','GET'])
def register():
    ph = PasswordHasher()
    engine = create_engine("mysql+mysqlconnector://root:Printhelloworld1!@127.0.0.1/users", echo=True)
    users = engine.connect()
    x = 1
    session['username'] = request.form.get('User')
    username = session['username']
    if username == None:
        return render_template('Register.html')
    else:
        while x == 1:
            user = pd.read_sql('SELECT * FROM users.users;',users)
            app.logger.debug(user)
            app.logger.debug(username)
            if username in user.values:
                return render_template('RegisterUserTaken.html')
            else:
                username = username.lower()
                password = request.form.get('Password')
                password = ph.hash(password)
                users.execute(text('INSERT INTO `users`.`users` (`Username`, `Password`) VALUES (:Username, :Password)'),
                         {'Username':username,'Password':password})
                users.commit()
                mydb = mysql.connector.connect(host='127.0.0.1',user='root',password='Printhelloworld1!')
                mycursor = mydb.cursor()
                mycursor.execute(f'CREATE DATABASE {username}')
                mydb.close
                engine = create_engine(f"mysql+mysqlconnector://root:Printhelloworld1!@127.0.0.1/{username}", echo=True)
                finance_app = engine.connect()
                finance_app.execute(text(f"""CREATE TABLE {username}.`accounts` (`idaccounts` INT NOT NULL AUTO_INCREMENT,`Account` VARCHAR(45) NOT NULL,`Account Type` VARCHAR(45) NOT NULL,PRIMARY KEY (`idaccounts`),UNIQUE INDEX `Account_UNIQUE` (`Account` ASC) VISIBLE);"""))
                finance_app.execute(text(f"""CREATE TABLE {username}.`categories` (`idcategories` INT NOT NULL AUTO_INCREMENT,`Category` VARCHAR(45) NOT NULL,PRIMARY KEY (`idcategories`),UNIQUE INDEX `Category_UNIQUE` (`Category` ASC) VISIBLE);"""))
                finance_app.execute(text(f"""CREATE TABLE {username}.`investment transactions` (`idinvestment transactions` INT NOT NULL AUTO_INCREMENT,`Date` DATE NOT NULL,`Transaction` VARCHAR(45) NOT NULL,`Ticker` VARCHAR(45) NOT NULL,`Quantity` FLOAT NULL DEFAULT NULL,`Price` FLOAT NULL DEFAULT NULL,`Amount` FLOAT NOT NULL,`Account` VARCHAR(45) NOT NULL,PRIMARY KEY (`idinvestment transactions`));"""))
                finance_app.execute(text(f"""CREATE TABLE {username}.`investment_accounts` (`idinvestment_accounts` INT NOT NULL AUTO_INCREMENT,`Account` VARCHAR(45) NOT NULL,`Account Type` VARCHAR(45) NOT NULL,PRIMARY KEY (`idinvestment_accounts`),UNIQUE INDEX `Account_UNIQUE` (`Account` ASC) VISIBLE);"""))
                finance_app.execute(text(f"""CREATE TABLE {username}.`recurring_transactions` (`idrecurring_transactions` INT NOT NULL AUTO_INCREMENT,`Bill` VARCHAR(45) NOT NULL,`Frequency` VARCHAR(45) NOT NULL,`Start_Date` DATE NOT NULL,`Amount` FLOAT NOT NULL,`Account` VARCHAR(45) NOT NULL,PRIMARY KEY (`idrecurring_transactions`));"""))
                finance_app.execute(text(f"""CREATE TABLE {username}.`transactions` (`idtransactions` INT NOT NULL AUTO_INCREMENT,`Date` DATE NOT NULL,`Transaction` VARCHAR(45) NOT NULL,`Amount` FLOAT NOT NULL DEFAULT '0',`Category` VARCHAR(45) NOT NULL,`Account` VARCHAR(45) NOT NULL,PRIMARY KEY (`idtransactions`));"""))
                categories = ['Bars/Alcohol','Car Payment','Cash','CC Payment','CC Rewards','Coffee','Education','Fast Food','Grocieries','Insurance','Interest','Internet','Loan Payment','Medical','Misc','Paycheck','Phone','Refund/Rebate','Rent','Restaraunts','Shopping','Starting Balance','Streaming','Subscriptions','Transfer','Travel','Utilities','Taxes','Investment','Dividend','ATM','Pets']
                for i in categories:
                    finance_app.execute(text(f"""INSERT INTO {username}.`categories` (`Category`) VALUES ('{i}');"""))
                finance_app.execute(text(f"""CREATE TABLE {username}.`budget` (`idbudget` INT NOT NULL AUTO_INCREMENT,`Category` VARCHAR(45) NOT NULL,`Budget` FLOAT NOT NULL DEFAULT 0,`budgetcol` VARCHAR(45) NULL,PRIMARY KEY (`idbudget`));"""))
                budcat = ['Income','Bars/Alcohol','Car Payment','Coffee','Education','Fast Food','Grocieries','Insurance','Internet','Loan Payment','Medical','Phone','Rent','Restaraunts','Shopping','Streaming','Subscriptions','Travel','Utilities','Pets']
                for i in budcat:
                    finance_app.execute(text(f"""INSERT INTO {username}.`budget` (`Category`) VALUES ('{i}');"""))
                finance_app.execute(text(f"""INSERT INTO {username}.`transactions` (`Date`, `Transaction`, `Amount`, `Category`, `Account`) VALUES ('2025-01-01', 'Temp', '0.00', 'Misc', 'Temp');"""))
                finance_app.commit()
                users.close()
                finance_app.close()
                x = 0
                return redirect(url_for('BalanceTracking'))

@app.route('/LogOut')
def LogOut():
    session['username'] = ''
    return redirect(url_for('signin'))

def Bill(x,y):
    username = session['username']
    engine = create_engine(f"mysql+mysqlconnector://root:Printhelloworld1!@127.0.0.1/{username}", echo=True)
    finance_app = engine.connect()
    Bills = pd.read_sql(f'SELECT * FROM {username}.recurring_transactions;',finance_app)
    Bills = Bills.rename(columns={'Start_Date':'Next Date'})
    Bills = Bills[Bills['idrecurring_transactions']==x]
    if y == 'Bill':
        Bill = Bills.iat[0,1]
    elif y == 'Frequency':
        Bill = Bills.iat[0,2]
    elif y == 'Date':
        Bill = Bills.iat[0,3]
    elif y == 'Amount':
        Bill = Bills.iat[0,4]
    elif y == 'Account':
        Bill = Bills.iat[0,5]
    finance_app.close()
    return Bill

def Balance_Tracking():
    username = session['username']
    engine = create_engine(f"mysql+mysqlconnector://root:Printhelloworld1!@127.0.0.1/{username}", echo=True)
    finance_app = engine.connect()
    transactions = pd.read_sql('SELECT * from transactions;',finance_app)
    transactions['Date'] = pd.to_datetime(transactions['Date'])
    Balances = transactions.groupby(['Account'])['Amount'].sum()
    Balances = Balances.to_frame()
    Balances = Balances.reset_index()
    Balances['Amount'] = Balances['Amount'].round(2)
    accts = Balances['Account'].unique()
    Daily = pd.DataFrame(columns=['Date','Transaction','Amount'])
    for x in range(0,365):
        datet = date.today()+datetime.timedelta(days=1)*x
        da = pd.DataFrame([[datet,'Daily',0]],columns=['Date','Transaction','Amount'])
        Daily = pd.concat([Daily,da])
    BalanceTracking = pd.DataFrame(columns=['Date','Transaction','Amount','Balance','Account'])
    for i in accts:
        account = i
        Bills = pd.read_sql(f'SELECT * FROM {username}.recurring_transactions;',finance_app)
        Bills = Bills.drop(columns=['idrecurring_transactions'])
        Bills = Bills[Bills['Account']==account]
        df = Balances[Balances['Account']==account]
        df = df.rename(columns={'Balance':'Amount'})
        for index, row in Bills.iterrows():
            frequency = row['Frequency']
            startdate = row['Start_Date']
            payee = row['Bill']
            amount = row['Amount']
            acct = row['Account']
            if frequency == 'Bi Weekly':
                for i in range(0,26):
                    bill = pd.DataFrame([[startdate+datetime.timedelta(days=14)*i,payee,amount]],columns=['Date','Transaction','Amount'])
                    df = pd.concat([df,bill])
            elif frequency == 'Monthly':
                for i in range(0,12):
                    bill = pd.DataFrame([[startdate+relativedelta(months=1)*i,payee,amount]],columns=['Date','Transaction','Amount'])
                    df = pd.concat([df,bill])
            elif frequency == 'Daily':
                for i in range(0,365):
                    bill = pd.DataFrame([[startdate+datetime.timedelta(days=1)*i,payee,amount]],columns=['Date','Transaction','Amount'])
                    df = pd.concat([df,bill])
            elif frequency == 'Anually':
                for i in range(0,1):
                    bill = pd.DataFrame([[startdate+datetime.timedelta(days=365)*i,payee,amount]],columns=['Date','Transaction','Amount'])
                    df = pd.concat([df,bill])
            elif frequency == 'One Time':
                bill = pd.DataFrame([[startdate,payee,amount]],columns=['Date','Transaction','Amount'])
                df = pd.concat([df,bill])      
        df = pd.concat([Daily,df])
        df = df.sort_values(by=['Date','Amount'],ascending=[True,False],na_position='first')
        df['Balance'] = df['Amount'].cumsum()
        df['Account'] = account
        BalanceTracking = pd.concat([BalanceTracking,df])
    BalanceTrack = BalanceTracking
    BalanceTrack['Amount'] = BalanceTrack['Amount'].apply(lambda x: f"${x:,.2f}")
    BalanceTrack['Balance'] = BalanceTrack['Balance'].apply(lambda x: f"${x:,.2f}")
    finance_app.close()
    return BalanceTrack

def Transact():
    username = session['username']
    app.logger.debug(username)
    engine = create_engine(f"mysql+mysqlconnector://root:Printhelloworld1!@127.0.0.1/{username}", echo=True)
    finance_app = engine.connect()
    transactions = pd.read_sql('SELECT * from transactions;',finance_app)
    transaction = transactions
    finance_app.close()
    return transaction

def Bud():
    username = session['username']
    engine = create_engine(f"mysql+mysqlconnector://root:Printhelloworld1!@127.0.0.1/{username}", echo=True)
    finance_app = engine.connect()
    bud = pd.read_sql('SELECT * from budget;',finance_app)
    finance_app.close()
    return bud

def Balances():
    transactions = Transact()
    balance = transactions.groupby('Account')['Amount'].sum()
    balance = balance.to_frame()
    balance = balance.reset_index()
    balance = balance.rename(columns={'Amount':'Balance'})
    balance['Balance'] = balance['Balance'].apply(lambda x: f"${x:,.2f}")
    return balance

def Account():
    username = session['username']
    engine = create_engine(f"mysql+mysqlconnector://root:Printhelloworld1!@127.0.0.1/{username}", echo=True)
    finance_app = engine.connect()
    account = pd.read_sql('SELECT * from accounts;',finance_app)
    finance_app.close()
    return account

def Categories():
    username = session['username']
    engine = create_engine(f"mysql+mysqlconnector://root:Printhelloworld1!@127.0.0.1/{username}", echo=True)
    finance_app = engine.connect()
    categories = pd.read_sql(f'SELECT * FROM {username}.categories;',finance_app)
    categories = categories.drop(columns=['idcategories'])
    categories = categories['Category'].unique()
    categories = np.sort(categories)
    finance_app.close()
    return categories
            
@app.route('/BalanceTracking', methods=['POST','GET'])
def BalanceTracking():
    username = session['username']
    engine = create_engine(f"mysql+mysqlconnector://root:Printhelloworld1!@127.0.0.1/{username}", echo=True)
    finance_app = engine.connect()
    BalanceTrack = Balance_Tracking()
    account = Account()
    account = account['Account'].unique()
    account = np.sort(account)
    account = np.insert(account, 0, 'All')
    Bills = pd.read_sql(f'SELECT * FROM {username}.recurring_transactions;',finance_app)
    Bills = Bills.rename(columns={'Start_Date':'Next Date'})
    Bills['Amount'] =  Bills['Amount'].apply(lambda x: f"${x:,.2f}")
    recacct = Bills['Account'].unique()
    recacct = np.sort(recacct)
    recacct = np.insert(recacct, 0, 'All')
    acct = request.form.get('Account')
    timeframe = request.form.get('Timeframe')
    if acct == None:
        acct = 'All'
    if timeframe == None:
        timeframe = 'Year'
    table1 = Bills
    table1['Edit'] = table1['idrecurring_transactions'].apply(lambda x: f'<button onclick="editrecurring({x},\'{Bill(x,'Bill')}\',\'{Bill(x,'Frequency')}\',\'{Bill(x,'Date')}\',\'{Bill(x,'Amount')}\',\'{Bill(x,'Account')}\')" style="padding: 5px 10px; background-color: #28a745; color: #fff; border: none; border-radius: 5px;" class="btn">Edit</button>')
    table1['Delete'] = table1['idrecurring_transactions'].apply(lambda x: f'<form action="/recurringtrandel/" method="POST" onsubmit="return confirm(\'Are you sure?\');"><input type="hidden" name="ID" value="{x}"><button type="submit" class="btn">Delete</button></form>')
    table1['Mark Paid'] = table1['idrecurring_transactions'].apply(lambda x: f'<form action="/recurringtranpaid/" method="POST"><input type="hidden" name="ID" value="{x}"><button type="submit" class="btn">Mark Paid</button></form>')
    table1 = table1.sort_values(by=['Next Date'])
    table1 = table1.drop(columns=['idrecurring_transactions'])
    table1 = table1.to_html(classes='table table-stripped',escape=False,index=False,table_id='Bills Table')
    table2 = BalanceTrack
    if acct == 'All':
        table2=table2
    else:
        table2 = table2[table2['Account']==acct]
    if timeframe == 'Month':
        datefilter = date.today() + relativedelta(months=1)
        table2 = table2[table2['Date']<datefilter]
    elif timeframe == '3 Months':
        datefilter = date.today() + relativedelta(months=3)
        table2 = table2[table2['Date']<datefilter]
    elif timeframe == '6 Months':
        datefilter = date.today() + relativedelta(months=6)
        table2 = table2[table2['Date']<datefilter]
    else:
        table2 = table2
    table2 = table2.sort_values(by=['Date'])
    graph = px.line(table2, x='Date',y='Balance', title=acct, color='Account')
    graph.update_layout(autotypenumbers='convert types',yaxis_tickprefix ='$',yaxis_tickformat=',.2f',height=575)
    graph = graph.to_html()
    table2 = table2.dropna()
    table2 = table2[table2['Transaction']!='Daily']
    table2 = table2.to_html(classes='table table-stripped',escape=False,index=False,table_id='Tracking')
    finance_app.close()
    return render_template('BalanceTracking.html', Bills = table1, Tracking = table2, acct = acct, account = recacct,
    graph_json = graph, allacct = account, timeframe = timeframe)

@app.route('/addaccount/', methods=['POST'])
def addacct():
    username = session['username']
    engine = create_engine(f"mysql+mysqlconnector://root:Printhelloworld1!@127.0.0.1/{username}", echo=True)
    finance_app = engine.connect()
    if request.method == 'POST':
        Account = request.form.get('Account')
        AccountType = request.form.get('AccountType')
        OpenDate = request.form.get('OpenDate')
        StartingBal = request.form.get('StartingBalance')
        finance_app.execute(text(f'INSERT INTO {username}.`accounts` (`Account`, `Account Type`) VALUES (:Account, :AccountType)'),
                         {'Account':Account,'AccountType':AccountType})
        finance_app.execute(text(f"""INSERT INTO {username}.`transactions` (`Date`, `Transaction`, `Amount`, `Category`, `Account`) VALUES (:Date, 'Starting Balance', :Amount, 'Starting Balance', :Account);"""),
                         {'Date':OpenDate,'Account':Account,'Amount':StartingBal})
        finance_app.commit()
        finance_app.close()
        return redirect(url_for('BalanceTracking'))

@app.route('/recurringtran/', methods=['POST'])
def rectran():
    username = session['username']
    engine = create_engine(f"mysql+mysqlconnector://root:Printhelloworld1!@127.0.0.1/{username}", echo=True)
    finance_app = engine.connect()
    if request.method == 'POST':
        Bill = request.form.get('Bill')
        Frequency = request.form.get('Frequency')
        StartDate = request.form.get('Date')
        Amount = request.form.get('Amount')
        Account = request.form.get('Account')
        finance_app.execute(text(f'INSERT INTO {username}.`recurring_transactions` (`Bill`, `Frequency`, `Start_Date`, `Amount`, `Account`) VALUES (:Bill, :Frequency, :Start_Date, :Amount, :Account)'),
                         {'Bill':Bill,'Frequency':Frequency,'Start_Date':StartDate,'Amount':Amount,'Account':Account})
        finance_app.commit()
        finance_app.close()
        return redirect(url_for('BalanceTracking'))

@app.route('/recurringtrandel/', methods=['POST'])
def rectrandel():
    username = session['username']
    engine = create_engine(f"mysql+mysqlconnector://root:Printhelloworld1!@127.0.0.1/{username}", echo=True)
    finance_app = engine.connect()
    if request.method == 'POST':
        Bill = request.form.get('ID')
        finance_app.execute(text(f"DELETE FROM {username}.`recurring_transactions` WHERE (`idrecurring_transactions` = :Bill)"),{'Bill':Bill})
        finance_app.commit()
        finance_app.close()
        return redirect(url_for('BalanceTracking'))
    
@app.route('/recurringtranpaid/', methods=['POST'])
def rectranpaid():
    username = session['username']
    engine = create_engine(f"mysql+mysqlconnector://root:Printhelloworld1!@127.0.0.1/{username}", echo=True)
    finance_app = engine.connect()
    if request.method == 'POST':
        Bills = pd.read_sql(f'SELECT * FROM {username}.recurring_transactions;',finance_app)
        Bills = Bills.rename(columns={'Start_Date':'Next Date'})
        Bills['Amount'] =  Bills['Amount'].apply(lambda x: f"${x:,.2f}")
        Bills['Next Date'] = pd.to_datetime(Bills['Next Date'])
        ID = int(request.form.get('ID'))
        Bills = Bills[Bills['idrecurring_transactions']==ID]
        Bill = Bills.iat[0,1]
        Frequency = Bills.iat[0,2]
        StartDate = Bills.iat[0,3]
        Amount = Bills.iat[0,4]
        Account = Bills.iat[0,5]
        print(Frequency)
        if Frequency == 'One Time':
            finance_app.execute(text(f"DELETE FROM {username}.`recurring_transactions` WHERE (`idrecurring_transactions` = :Bill)"),{'Bill':ID})
        elif Frequency == 'Weekly':
            NewDate = StartDate + timedelta(days=7)
            finance_app.execute(text(f"UPDATE {username}.`recurring_transactions` SET `Start_Date` = :Date WHERE (`idrecurring_transactions` = :Bill)"),{'Bill':ID,'Date':NewDate})
        elif Frequency == 'Bi Weekly':
            NewDate = StartDate + timedelta(days=14)
            finance_app.execute(text(f"UPDATE {username}.`recurring_transactions` SET `Start_Date` = :Date WHERE (`idrecurring_transactions` = :Bill)"),{'Bill':ID,'Date':NewDate})
        elif Frequency == 'Monthly':
            NewDate = StartDate + relativedelta(months=1)
            finance_app.execute(text(f"UPDATE {username}.`recurring_transactions` SET `Start_Date` = :Date WHERE (`idrecurring_transactions` = :Bill)"),{'Bill':ID,'Date':NewDate})
        elif Frequency == 'Anually':
            NewDate = StartDate + timedelta(days=365)
            finance_app.execute(text(f"UPDATE {username}.`recurring_transactions` SET `Start_Date` = :Date WHERE (`idrecurring_transactions` = :Bill)"),{'Bill':ID,'Date':NewDate})
        finance_app.commit()
        finance_app.close()
        return redirect(url_for('BalanceTracking'))
    
@app.route('/recurringtranedit/', methods=['POST','GET'])
def rectranedit():
    username = session['username']
    engine = create_engine(f"mysql+mysqlconnector://root:Printhelloworld1!@127.0.0.1/{username}", echo=True)
    finance_app = engine.connect()
    if request.method == 'POST':
        ID = request.form.get('ID')
        Bill = request.form.get('Bill')
        Frequency = request.form.get('Frequency')
        StartDate = request.form.get('Date')
        Amount = request.form.get('Amount')
        Account = request.form.get('Account')
        finance_app.execute(text(f'UPDATE {username}.`recurring_transactions` SET `Bill` = :Bill, `Frequency` = :Frequency, `Start_Date` = :Start_Date, `Amount` = :Amount, `Account` = :Account WHERE (`idrecurring_transactions` = :ID);'),
                         {'ID':ID,'Bill':Bill,'Frequency':Frequency,'Start_Date':StartDate,'Amount':Amount,'Account':Account})
        finance_app.commit()
        finance_app.close()
        return redirect(url_for('BalanceTracking'))       

@app.route('/Transactions/', methods=['POST','GET'])
def Transactions():
    table = Transact()
    account = Account()
    account = account['Account'].unique()
    account = np.sort(account)
    account = np.insert(account, 0, 'All')
    categories = Categories()
    balance = Balances()
    balance = balance.to_html(escape=False,index=False,table_id='Balance').replace('<td>', '<td align="right">')
    acct = request.form.get('Account')
    if acct == None:
        acct = 'All'
    table['Edit'] = table['idtransactions'].apply(lambda x: f'<button onclick="edittran({x},\'{trans(x,'Date',table)}\',\'{trans(x,'Transaction',table)}\',\'{trans(x,'Amount',table)}\',\'{trans(x,'Category',table)}\',\'{trans(x,'Account',table)}\')" style="padding: 10px 20px; background-color: #28a745; color: #fff; border: none; border-radius: 5px;">Edit</button>')
    table['Delete'] = table['idtransactions'].apply(lambda x: f'<form action="/trandel/" method="POST" onsubmit="return confirm(\'Are you sure?\');"><input type="hidden" name="ID" value="{x}"><button type="submit">Delete</button></form>')
    table['Amount'] = table['Amount'].apply(lambda x: f"${x:,.2f}")
    table = table.drop(columns=['idtransactions'])
    table = table.sort_values(by=['Date'],ascending=False)
    if acct == 'All':
        table = table.to_html(classes='table table-stripped',escape=False,index=False,table_id='transactions table')
    else:
        table = table[table['Account']==request.form.get('Account')]
        table = table.to_html(classes='table table-stripped',escape=False,index=False,table_id='transactions table')
    return render_template('Transactions.html',account = account, table = table, acct = acct, categories = categories,balance = balance)

@app.route('/trandel/', methods=['POST'])
def trandel():
    username = session['username']
    engine = create_engine(f"mysql+mysqlconnector://root:Printhelloworld1!@127.0.0.1/{username}", echo=True)
    finance_app = engine.connect()
    if request.method == 'POST':
        Tran = request.form.get('ID')
        finance_app.execute(text(f"DELETE FROM {username}.`transactions` WHERE (`idTransactions` = :Tran)"),{'Tran':Tran})
        finance_app.commit()
        finance_app.close()
        return redirect(url_for('Transactions'))

@app.route('/tranadd/', methods=['POST','GET'])
def tranadd():
    username = session['username']
    engine = create_engine(f"mysql+mysqlconnector://root:Printhelloworld1!@127.0.0.1/{username}", echo=True)
    finance_app = engine.connect()
    if request.method == 'POST':
        Date = request.form.get('Date')
        Transaction = request.form.get('Transaction')
        Amount = request.form.get('Amount')
        Category = request.form.get('Category')
        Account = request.form.get('Account')
        finance_app.execute(text(f"""INSERT INTO {username}.`transactions` (`Date`, `Transaction`, `Amount`, `Category`, `Account`) VALUES (:Date, :Transaction, :Amount, :Category, :Account)"""),
                         {'Date':Date,'Transaction':Transaction,'Amount':Amount,'Category':Category,'Account':Account})
        finance_app.commit()
        finance_app.close()
        return redirect(url_for('Transactions'))

@app.route('/tranedit/', methods=['POST','GET'])
def tranedit():
    username = session['username']
    engine = create_engine(f"mysql+mysqlconnector://root:Printhelloworld1!@127.0.0.1/{username}", echo=True)
    finance_app = engine.connect()
    if request.method == 'POST':
        ID = request.form.get('ID')
        Date = request.form.get('Date1')
        Transaction = request.form.get('Transaction1')
        Amount = request.form.get('Amount1')
        Category = request.form.get('Category1')
        Account = request.form.get('Account1')
        finance_app.execute(text(f"""UPDATE {username}.`transactions` SET `Date` = :Date, `Transaction` = :Transaction, `Amount` = :Amount, `Category` = :Category, `Account` = :Account WHERE (`idTransactions` = :ID);"""),
                         {'ID':ID,'Date':Date,'Transaction':Transaction,'Amount':Amount,'Category':Category,'Account':Account})
        finance_app.commit()
        finance_app.close()
        return redirect(url_for('Transactions')) 

@app.route('/tranupload/', methods=['POST','GET'])
def tranupload():
    username = session['username']
    engine = create_engine(f"mysql+mysqlconnector://root:Printhelloworld1!@127.0.0.1/{username}", echo=True)
    finance_app = engine.connect()
    if request.method == 'POST':
        csv = request.files.get('CSV')
        csv_df = pd.read_csv(csv)
        csv_df = csv_df.dropna()
        for index, row in csv_df.iterrows():
            Date = row['Date']
            Transaction = row['Transaction']
            Amount = row['Amount']
            Category = row['Category']
            Account = row['Account']
            finance_app.execute(text(f"""INSERT INTO {username}.`transactions` (`Date`, `Transaction`, `Amount`, `Category`, `Account`) VALUES (:Date, :Transaction, :Amount, :Category, :Account)"""),
                            {'Date':Date,'Transaction':Transaction,'Amount':Amount,'Category':Category,'Account':Account})
        finance_app.commit()
        finance_app.close()
        return redirect(url_for('Transactions'))

def Buded(x):
    Buds = Bud()
    Buds = Buds[Buds['idbudget']==x]
    Buds = Buds.iat[0,2]
    app.logger.debug(Buds)
    return Buds


@app.route('/Budget', methods=['POST','GET'])
def Budget():
    username = session['username']
    year = request.form.get('Year')
    month = request.form.get('Month')
    bud = Bud()
    income = bud[bud['Category']=='Income']
    income = income.iat[0,2]
    app.logger.debug(income)
    today = date.today()
    currentmon = today.month
    currentyear = today.year
    transactions = Transact()
    transactions['Month'] = pd.to_datetime(transactions['Date']).dt.month
    transactions['Year'] = pd.to_datetime(transactions['Date']).dt.year
    account = Account()
    account = pd.DataFrame(account)
    transactions = pd.merge(transactions,account,on='Account',how='right')
    accttran = transactions
    accttran = accttran[accttran['Account Type']=='Credit Card']
    accttran = accttran[accttran['Category']!='CC Payment']
    accttran = accttran.groupby(['Year','Month','Account'])['Amount'].sum()
    accttran = accttran.to_frame()
    accttran = accttran.reset_index()
    transactions = transactions[transactions['Account Type'].isin(['Checking','Credit Card','Savings'])]
    transactions = transactions.groupby(['Year','Month','Category'])['Amount'].sum()
    transactions = transactions.to_frame()
    transactions = transactions.reset_index()
    transactions['Amount'] = transactions['Amount'].round(2)
    transactions = transactions[transactions['Category'].isin(['Bars/Alcohol','Car Payment','Coffee','Fast Food',
                                                                'Grocieries','Insurance','Interest','Internet',
                                                                'Loan Payment','Misc','Rent','Restaraunts','Shopping',
                                                                'Streaming','Travel','Utilities'])]
    years = transactions['Year'].unique()
    years = np.sort(years)
    if income is None:
        income = 0
    else:
        income = income
    if year is None:
        mon = int(currentmon)
        monstr = calendar.month_name[mon]
        y = currentyear
        y = int(y)
        transactions = transactions[transactions['Year']==y]
        transactions = transactions[transactions['Month']==mon]
        accttran = accttran[accttran['Year']==y]
        accttran = accttran[accttran['Month']==mon]
    else:
        mon = int(month)
        monstr = calendar.month_name[mon]
        y = year
        y = int(y)
        transactions = transactions[transactions['Year']==y]
        transactions = transactions[transactions['Month']==mon]
        accttran = accttran[accttran['Year']==y]
        accttran = accttran[accttran['Month']==mon]
    accttrantot = accttran['Amount'].sum()
    accttran.loc['Total','Amount'] = accttrantot
    transactions = transactions.drop(columns=['Year','Month'])
    accttran = accttran.drop(columns=['Year','Month'])
    accttran = accttran.fillna('Total')
    transactions = pd.merge(transactions,bud,on='Category',how='right')
    transactions = transactions[transactions['Category']!='Income']
    transactions = transactions.fillna(0)
    transactionstot = transactions['Amount'].sum()
    budgettot = transactions['Budget'].sum()
    monbud = budgettot
    remaining = income - monbud
    income = f"${income:,.2f}"
    monbud = f"${monbud:,.2f}"
    remaining = f"${remaining:,.2f}"
    transactions['Edit'] = transactions['idbudget'].apply(lambda x: f'<button onclick="editbudget({x},\'{Buded(x)}\')">Edit</button>')
    transactions.loc['Total','Amount'] = transactionstot
    transactions.loc['Total','Budget'] = budgettot
    transactions['Amount'] = transactions['Amount']*(-1)
    transactions['Remaining'] = transactions['Budget'] - transactions['Amount']
    transactions['Amount'] = transactions['Amount'].apply(lambda x: f"${x:,.2f}")
    transactions['Budget'] = transactions['Budget'].apply(lambda x: f"${x:,.2f}")
    transactions['Remaining'] = transactions['Remaining'].apply(lambda x: f"${x:,.2f}")
    accttran['Amount'] = accttran['Amount'].apply(lambda x: f"${x:,.2f}")
    transactions = transactions.drop(columns=['idbudget'])
    transactions = transactions.fillna('Total')
    transactions = transactions[['Category','Amount','Budget','Remaining','Edit']]
    transactions = transactions.to_html(escape=False,index=False,table_id='Budget')
    accttran = accttran.to_html(escape=False,index=False,table_id='accttran')
    return render_template('budget.html',transactions=transactions,mon=mon,year=y,monstr=monstr,accttran = accttran,income = income,monbud = monbud,remaining=remaining)

@app.route('/editbudget/', methods=['POST','GET'])
def editbudget():
    username = session['username']
    engine = create_engine(f"mysql+mysqlconnector://root:Printhelloworld1!@127.0.0.1/{username}", echo=True)
    finance_app = engine.connect()
    if request.method=='POST':
        ID = request.form.get('I')
        budget = request.form.get('Budget')
        finance_app.execute(text(f"""UPDATE {username}.`budget` SET `Budget` = :Budget WHERE (`idbudget` = :ID);"""),
                         {'ID':ID,'Budget':budget})
        finance_app.commit()
        finance_app.close()
        return redirect(url_for('Budget'))

@app.route('/editincome/', methods=['POST','GET'])
def editincome():
    username = session['username']
    engine = create_engine(f"mysql+mysqlconnector://root:Printhelloworld1!@127.0.0.1/{username}", echo=True)
    finance_app = engine.connect()
    if request.method=='POST':
        Income = request.form.get('Income')
        finance_app.execute(text(f"""UPDATE {username}.`budget` SET `Budget` = :Budget WHERE (`Category` = :ID);"""),
                         {'ID':'Income','Income':Income})
        finance_app.commit()
        finance_app.close()
        return redirect(url_for('Budget'))

@app.route('/Investments/')
def Investment():
    investments = investment_transactions.groupby(['Account','Ticker'])['Quantity'].sum()
    investmnets = investments.to_frame()
    investments = investments.reset_index()
    investments['Quantity'] = investments['Quantity'].round(4)
    tickers = investments['Ticker'].tolist()
    tickers = list(filter(None,tickers))
    tickers = list(set(tickers))
    StockPrices = pd.DataFrame(columns=['Ticker','Price'])
    for i in tickers:
        ticker = yf.Ticker(i).info
        Prices = {'Ticker':[i],'Price':[ticker['regularMarketPrice']]}
        Prices = pd.DataFrame(data=Prices)
        StockPrices = pd.concat([StockPrices,Prices])
    investments = pd.merge(StockPrices,investments,on=['Ticker'],how='right')
    investments = investments[['Account','Ticker','Quantity','Price']]
    investments['Balance'] = investments['Quantity'] * investments['Price']
    investments = investments[investments['Balance']>0.01]
    investments['Price'] = investments['Price'].round(2)
    investments['Balance'] = investments['Balance'].round(2)
    investments.loc['Total', 'Balance'] = investments['Balance'].sum()
    investments['Price'] = investments['Price'].apply(lambda x: f"${x:,.2f}")
    investments['Balance'] = investments['Balance'].apply(lambda x: f"${x:,.2f}")
    investments = investments.fillna('')
    investments = investments.to_html(classes='table table-stripped',escape=False,index=False,table_id='investments table').replace('<td>', '<td align="right">')
    return render_template('Investments.html',investment = investments)

if __name__ == '__main__':

    app.run(host='0.0.0.0')




