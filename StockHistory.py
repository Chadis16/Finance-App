from DB_connection import yf,date,pd
from Investments import tickers

StockHistory = pd.DataFrame(columns=['Date','Ticker','Close'])
for row in tickers:
    df = yf.download(row,start='2024-12-31',end=date.today())
    df = df['Close']
    df['Ticker'] = row
    df = df.reset_index()
    df = df.rename(columns={row:'Close'})
    StockHistory = pd.concat([StockHistory,df])

