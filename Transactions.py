from DB_connection import finance_app,pd,datetime, np

transactions = pd.read_sql('SELECT * from transactions;',finance_app)
#transactions = transactions.drop(columns=['idTransactions'])
transactions['Date'] = pd.to_datetime(transactions['Date'])
transaction = transactions
account = transactions['Account'].unique()
account = np.sort(account)
account = np.insert(account, 0, 'All')

Balances = transactions.groupby(['Account'])['Amount'].sum()
Balances = Balances.to_frame()
Balances = Balances.reset_index()
Balances['Amount'] = Balances['Amount'].round(2)