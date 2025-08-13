from DB_connection import finance_app,pd,date,yf,datetime
Holidays = ['2025-01-01',
            '2025-01-09',
            '2025-02-17',
            '2025-04-18',
            '2025-05-26',
            '2025-06-19',
            '2025-07-04',
            '2025-08-01',
            '2025-11-27',
            '2025-12-25']
Holidays = pd.to_datetime(Holidays)

accounts = pd.read_sql('SELECT * FROM finance_app.accounts;',finance_app)
accounts = accounts.drop(columns=['idnew_table'])

print(accounts)

