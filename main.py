from fastapi import FastAPI
from pydantic import BaseModel
from datetime import datetime

app = FastAPI()

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
        data["Accounts"].append(account.model_dump_json())
        with open(self.db_path,"w") as file:
            self.json.dump(data,file,indent=4)

    def writeInvoice(self, invoice : "Invoice"):
        data = self.readDB()
        data["Invoices"].append(invoice.model_dump_json())
        with open(self.db_path,"w") as file:
            self.json.dump(data,file,indent=4)

class Account(BaseModel):
    name : str

class Invoice(BaseModel):
    sender : Account
    receiver : Account
    amount : float
    due : datetime
    issued : datetime

