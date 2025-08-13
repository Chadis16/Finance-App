from DB_connection import pd,date,datetime,relativedelta,finance_app
from Transactions import transactions
from Daily import Daily

accounts = pd.read_sql('SELECT * FROM finance_app.accounts;',finance_app)
accounts = accounts.drop(columns=['idnew_table'])

AcctBalances = pd.DataFrame(columns=['Date','Balance','Account','Account Type'])
for index, row in accounts.iterrows():
    account = row['Account']
    accounttype =  row['Account Type']
    trans = transactions[transactions['Account']==account]
    trans = pd.concat([Daily,trans])
    trans['Date'] = pd.to_datetime(trans['Date'])
    trans = trans.sort_values(by=['Date','Amount'],ascending=[True,False])
    trans['Balance'] = trans['Amount'].cumsum()
    trans = trans.groupby(['Date'])['Balance'].min()
    trans = trans.to_frame()
    trans['Account'] = account
    trans['Account Type'] = accounttype
    trans = trans.reset_index()
    AcctBalances = pd.concat([AcctBalances,trans])
AcctBalances = AcctBalances[AcctBalances['Date']>'2024-12-31']
AcctBalances['Edit'] = AcctBalances['Account'].apply(lambda x: f'<button onclick="alert(\'Button for Ticker: {x} clicked!\')">Click Me</button>')
AcctBalances = AcctBalances.to_html(classes='table table-stripped',escape=False,index=False)
