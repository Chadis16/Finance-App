from DB_connection import pd,date,datetime,relativedelta,finance_app
from Transactions import Balances

accts = Balances['Account'].unique()
Daily = pd.DataFrame(columns=['Date','Transaction','Amount'])
for x in range(0,365):
    datet = date.today()+datetime.timedelta(days=1)*x
    da = pd.DataFrame([[datet,'Daily',0]],columns=['Date','Transaction','Amount'])
    Daily = pd.concat([Daily,da])
BalanceTracking = pd.DataFrame(columns=['Date','Transaction','Amount','Balance','Account'])
for i in accts:
    account = i
    Bills = pd.read_sql('SELECT * FROM finance_app.recurring_transactions;',finance_app)
    Bills = Bills.drop(columns=['idrecurring transactions'])
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