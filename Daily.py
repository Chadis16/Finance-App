from DB_connection import date,pd,datetime
today = date.today()
Daily = pd.DataFrame(columns=['Date','Transaction','Amount'])
for i in range((today-datetime.date(2024,5,29)).days):
    date = today - datetime.timedelta(days=i)
    d = {'Date':date,'Transaction':'Daily','Amount':0}
    x = pd.DataFrame([data:=d])
    Daily = pd.concat([Daily,x])