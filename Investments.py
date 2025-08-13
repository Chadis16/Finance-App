from Investment_Transactions import investment_transactions
from DB_connection import pd,yf
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