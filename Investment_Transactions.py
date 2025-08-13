from DB_connection import pd,finance_app
investment_transactions = pd.read_sql('SELECT * FROM finance_app.`investment transactions`;',finance_app)
investment_transactions = investment_transactions.drop(columns=['idinvestment transactions'])
investment_transactions['Date'] = pd.to_datetime(investment_transactions['Date'])