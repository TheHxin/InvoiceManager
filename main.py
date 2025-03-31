from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, field_validator
from datetime import datetime
import json

 

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



app = FastAPI()
db = DataBase("./db.json")
accounts_list = db.readAccounts()

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


@app.get("/")
def index():
    return "service is started"

@app.get("/invoices")
def getInvoices() -> list[Invoice]:
    return db.readInvoices()

@app.get("/accounts")
def get_account() -> list[Account]:
    return db.readAccounts()

@app.post("/invoices")
def post_invoices(invoice : Invoice) -> Invoice:
    db.writeInvoice(invoice)
    return invoice

@app.post("/accounts")
def post_acccount(account : Account) -> Account:
    db.writeAccount(account)
    accounts_list.append(json.loads(account.model_dump_json()))
    return account
