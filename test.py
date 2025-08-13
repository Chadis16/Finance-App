from argon2 import PasswordHasher
from sqlalchemy import create_engine, insert, MetaData, Table, Column, Integer, String, DATE, FLOAT
import pandas as pd

# metadata = MetaData()
# engine = create_engine("mysql+mysqlconnector://root:Printhelloworld1!@127.0.0.1/users", echo=True)
# users = engine.connect()
# ph = PasswordHasher()
# res = ph.hash("TestPassword")
# print(res)
# test = pd.read_sql('SELECT * FROM users.users;',users)
# test = test[test['Username']=='Test']
# test = test.iat[0,2]
# try:
#     ph.verify(test, "TestPassword")
#     print("Success")
# except Exception:
#     print('Fail')

def login():
    engine = create_engine("mysql+mysqlconnector://root:Printhelloworld1!@127.0.0.1/users", echo=True)
    users = engine.connect()
    ph = PasswordHasher()
    res = ph.hash("TestPassword")
    test = pd.read_sql('SELECT * FROM users.users;',users)
    test = test[test['Username']=='Test']
    test = test.iat[0,2]
    try:
        ph.verify(test, "TestPasswor")
        return "Pass"
    except Exception:
        print('Fail')
        return "Fail"
    
Login = login()
if Login == 'Pass':
    print('Pass')
else:
    print("Fail")