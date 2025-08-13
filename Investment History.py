from Investment_Transactions import investment_transactions
from Daily import Daily
from DB_connection import pd,date,datetime,relativedelta,finance_app
from StockHistory import StockHistory
investment_accounts = pd.read_sql('SELECT * FROM finance_app.`investment_accounts`;',finance_app)
investment_accounts = investment_accounts.drop(columns=['idinvestment_accounts'])

Investment_Balances = pd.DataFrame(columns=['Date','Ticker','Shares','Close','Balance','Account Type'])

for index, row in investment_accounts.iterrows():
    accttotal = pd.DataFrame(columns=['Date','Ticker','Shares'])
    acct = row['Account']
    accttype = row['Account Type']
    trans = investment_transactions[investment_transactions['Account']==acct]
    cash = pd.concat([trans,Daily])
    cash['Date'] = pd.to_datetime(cash['Date'])
    cash = cash.sort_values(by=['Date','Amount'],ascending=[True,False])
    cash['Shares'] = cash['Amount'].cumsum()
    cash = cash.groupby(['Date'])['Shares'].min()
    cash = cash.to_frame()
    cash = cash.reset_index()
    cash = cash[cash['Date']>'2024-12-31']
    cash['Account'] = acct
    cash['Ticker'] = 'Cash'
    cash['Close'] = 1
    ticker = trans['Ticker'].unique()
    for row in ticker:
        stock = trans[trans['Ticker']==row]
        daily = Daily.rename(columns={'Amount':'Quantity','Transaction':'Ticker'})
        stock = pd.concat([daily,stock])
        stock['Date'] = pd.to_datetime(stock['Date'])
        stock = stock.sort_values(by=['Date','Quantity'],ascending=[True,False])
        stock['Shares'] = stock['Quantity'].cumsum()
        stock = stock.groupby(['Date'])['Shares'].min()
        stock = stock.to_frame()
        stock = stock.reset_index()
        stock['Ticker'] = row
        stock['Account'] = acct
        accttotal = pd.concat([accttotal,stock])
    accttotal = pd.merge(accttotal,StockHistory,how='right',on=['Date','Ticker'])
    accttotal = pd.concat([accttotal,cash])
    accttotal['Account Type'] = accttype
    Investment_Balances = pd.concat([Investment_Balances,accttotal])
Investment_Balances['Balance'] = Investment_Balances['Shares'] * Investment_Balances['Close']
Investment_Balances = Investment_Balances[(Investment_Balances['Balance']>0.01) | (Investment_Balances['Balance']<-0.01)]