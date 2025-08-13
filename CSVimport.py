from DB_connection import csv,pathlib,finance_app

csv_path = pathlib.Path.cwd() / "investment transactions (1).csv"
dict_list = list()
with csv_path.open(mode='r') as csv_reader:
    csv_reader = csv.reader(csv_reader)
    for rows in csv_reader:
        dict_list.append({'Date':rows[0], 'Transaction':rows[1],'Ticker':rows[2],'Quantity':rows[3],'Price':rows[4],'Amount':rows[5],'Account':rows[6]})
mycursor = finance_app.cursor()
for item in dict_list:
    sql = "INSERT INTO finance_app.`investment transactions`(Date, Transaction, Ticker, Quantity, Price, Amount, Account) VALUES(%s, %s, %s, %s, %s, %s, %s)"
    val = item['Date'], item['Transaction'], item['Ticker'], item['Quantity'], item['Price'], item['Amount'], item['Account']
    mycursor.execute(sql,val)
finance_app.commit()
mycursor.execute("SELECT * FROM finance_app.`investment transactions`;")
myresult = mycursor.fetchall()
for x in myresult:
    print(x)