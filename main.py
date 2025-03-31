from fastapi import FastAPI
from pydantic import BaseModel
from datetime import datetime



class DataBase():
    def __init__(self, db_path):
        import json
        self.db_path = db_path
        self.json = json
    
    def readDB(self):
        with open(self.db_path,"r") as file:
            data = self.json.load(file)
        return data
    
    def readAccounts(self):
        return self.readDB()["Accounts"]
    
    def readInvoices(self):
        return self.readDB()["Invoices"]
    
    def writeAccount(self, account : "Account"):
        data = self.readDB()
        data["Accounts"].append(self.json.loads(account.model_dump_json()))
        with open(self.db_path,"w") as file:
            self.json.dump(data,file,indent=4)

    def writeInvoice(self, invoice : "Invoice"):
        data = self.readDB()
        data["Invoices"].append(self.json.loads(invoice.model_dump_json()))
        with open(self.db_path,"w") as file:
            self.json.dump(data,file,indent=4)



app = FastAPI()
db = DataBase("./db.json")

class Account(BaseModel):
    name : str

class Invoice(BaseModel):
    sender : Account
    receiver : Account
    amount : str
    due : datetime
    issued : datetime

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
    return account
