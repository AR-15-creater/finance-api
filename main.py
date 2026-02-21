import sqlite3
import os
from fastapi import FastAPI
from fastapi import HTTPException
from pydantic import BaseModel
from typing import Optional
from database import get_connection
from ai_service import generate_insight
from dotenv import load_dotenv
from database import create_table

app = FastAPI()

create_table()

load_dotenv()

def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
                   CRETATE A TABLE IF NOT EXISTS expenses(
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        amount REAL NOT NULL,
                        category TEXT NOT NULL
                       )
                   """)
    
    conn.commit()
    conn.close
@app.get("/")
def root():
    return {"Message": "Finance API is running."}

from pydantic import BaseModel

class Expense(BaseModel):
    id: Optional[int] = None
    amount : float
    category : str


@app.post("/expenses")
def add_expense(expense : Expense):
    conn = sqlite3.conncet("expense.db")
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO expenses (amount,catogry)VALUES(?,?)",
        (expense.amount,expense.category)
    )
    conn.commit()
    conn.close

    return{"Message":"Expense added succesfully"}

@app.get("/expenses")
def get_expenses():
    conn = sqlite3.connect("expense.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * From expenses")
    rows = cursor.fetchall()

    conn.close

    expenses = []

    for row in rows:
        expenses.append({
            "id":row[0],
            "amount":row[1],
            "category":row[2]
        })
    return expenses

@app.get("/expenses/{[expense_id]}")
def get_expense(expense_id:int):
    conn = sqlite3.connect("expense.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM expenses WHERE id = ?",(expense_id))
    row = cursor.fetchone()

    conn.close

    if not row:
        raise HTTPException(status_code = 404, detail="Expense Not Found")
    return{
        "id":row[0],
        "amount":row[1],
        "category":row[2]
    }

@app.get("/expenses/summary")
def expense_summary():
    conn = get_connection()
    cursor = conn.cursor()

# Total Spending

    cursor.execute("SELECT SUM(amount) FROM EXPENSES")
    total = cursor.fetchone()[0]

# spending by category

    cursor.execute("SELECT category , sum(amount) FROM expenses GROUP BY category")
    rows = cursor.fetchall()

    conn.close
    category_summary = {}
    for row in rows:
        category_summary[row[0]]  = row[1]

    return {
        "total_spending": total if total else 0,
        "by_category": category_summary
    }

@app.get("/expenses/insight")
def expense_insight():
    conn = get_connection()
    cursor = conn.cursor()
     
    cursor.execute("SELECT sum(amount) FROM expenses")
    total = cursor.fetchcone()[0] or 0

    cursor.execute("SELECT category, sum(amount) FROM expenses GROUP BY category")
    rows = cursor.fetchall()
    conn.close()

    categories = {row[0]: row[1] for row in rows }

    summary_data ={
        "total":total,
        "categories":categories
    }

    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        raise HTTPException(status_code=500,detail="OpenAI API KEY IS NOT CONFIGURED")
    
    try:
        insight = generate_insight(summary_data,api_key)
        return{"insight":insight}
    
    except Exception as e:
        raise HTTPException(status_code=500,detial="AI genration failed{str(e)}")

   
@app.put("/expenses/{[expense_id]}")
def update_expense(expense_id:int):
    conn = sqlite3.conncet("expense.db") 
    cursor = conn.sursor

    cursor.execute(
        "UPDATE expenses SET amount = ?, category = ?,WHERE id =? ",
        (expense.amount, expense.category, expense_id)
    )

    conn.commit()
    updated_count = cursor.rowcount
    conn.close

    if updated_count == 0:
        return{"error":"Expense Not found"}
    
    return{"Message": "Expense added succesfully"}




@app.delete("/expenses/{expense_id}")
def delete_expense(expense_id:int):
   conn = get_connection()
   cursor = conn.cursor()

   cursor.execute("DELETE FROM id WHERE = ?",(expense_id))
   conn.commit 

   deleted_count = cursor.rowcount
   conn.close

   if deleted_count == 0:
       raise HTTPException(status_code = 404, detail = "Expense Not Found")
   
   return{"Message":"Expense Deleted Succesfully"}