from fastapi import FastAPI, HTTPException, Response, Cookie
from pydantic import BaseModel, field_validator
from datetime import datetime
import json
import bcrypt
import secrets

 

class DataBase():
    def __init__(self, db_path):
        self.db_path = db_path
    
    def readDB(self):
        with open(self.db_path,"r") as file:
            data = json.load(file)
        return data
    
    def readAccounts(self):
        return self.readDB()["Accounts"]
    
    def readInvoices(self):
        return self.readDB()["Invoices"]

    def readUsers(self):
        return self.readDB()["Users"]
    
    def writeAccount(self, account : "Account"):
        data = self.readDB()
        data["Accounts"].append(json.loads(account.model_dump_json()))
        with open(self.db_path,"w") as file:
            json.dump(data,file,indent=4)

    def writeInvoice(self, invoice : "Invoice"):
        data = self.readDB()
        data["Invoices"].append(json.loads(invoice.model_dump_json()))
        with open(self.db_path,"w") as file:
            json.dump(data,file,indent=4)

    def writeUser(self, user : "User"):
        data = self.readDB()
        data["Users"].append(json.loads(user.model_dump_json()))
        with open(self.db_path,"w") as file:
            json.dump(data,file,indent=4)

    

app = FastAPI()
db = DataBase("./db.json")
accounts_list = db.readAccounts()
logged_in : list["UserLogin"] = []

def genSessionKey() -> str:
    return secrets.token_hex(16)
def hashPassword(password) -> str:
    return bcrypt.hashpw(password, bcrypt.gensalt())
def checkPassword(password_plain, password_hashed) -> bool:
    return bcrypt.checkpw(password_plain, password_hashed)

class Account(BaseModel):
    name : str

class Invoice(BaseModel):
    sender : Account
    receiver : Account
    amount : str
    due : datetime
    issued : datetime

    @field_validator("sender", "receiver")
    def checkAccountExistance(cls , v : Account):
        if json.loads(v.model_dump_json()) not in accounts_list:
            raise ValueError("Account does not exist")
        return v
    
class User(BaseModel):
    username : str
    password : str

class UserLogin(User):
    session_key : str

    def __init__(self, key):
        self.session_key = key



@app.get("/")
def index():
    return "service is started"

@app.get("/invoices")
def get_invoices() -> list[Invoice]:
    return db.readInvoices()

@app.get("/accounts")
def get_account() -> list[Account]:
    return db.readAccounts()

@app.get("/login")
def get_login(resp = Response):
    ...

@app.post("/invoices")
def post_invoices(invoice : Invoice) -> Invoice:
    db.writeInvoice(invoice)
    return invoice

@app.post("/accounts")
def post_acccount(account : Account) -> Account:
    db.writeAccount(account)
    accounts_list.append(json.loads(account.model_dump_json()))
    return account

@app.post("/login")
def post_login(user : User, resp : Response) -> bool:
    users = db.readUsers()
    for i in users:
        if i["username"] == user.username:
            if checkPassword(user.password, i["password"]):
                session_key = genSessionKey()
                logged_in.append(UserLogin(session_key))
                resp.set_cookie(key="session_key",value=session_key,httponly=True,max_age=3600)
                return True
    return False
                