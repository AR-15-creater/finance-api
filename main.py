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
from pathlib import Path
from models import expense, Budget, User
from auth import hash_password, verify_password, create_access_token, verify_token
from fastapi import Depends
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

create_table()

app.mount("/frontend",
StaticFiles(directory="frontend"),
name ="frontend")

env_path=Path(__file__).parent / ".env"
load_dotenv(dotenv_path=env_path)
print("DEBUG API KEY:",os.getenv("OPENAI_API_KEY"))

def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
                   CREATE A TABLE IF NOT EXISTS expenses(
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
    conn = sqlite3.connect("expense.db")
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO expenses (amount, category)VALUES(?,?)",
        (expense.amount,expense.category)
    )
    conn.commit()
    conn.close()

    return{"Message":"Expense added succesfully"}

@app.post("/budgets")
def add_budget(budget: Budget):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO budgets(category, monthly_limit) VALUES (?, ?)",
        (budget.category,budget.monthly_limit)
    )
    conn.commit()
    conn.close()

    return{"Message":"Budget added succesfully"}

@app.post("/register")
def register(user: User):
    conn = get_connection()
    cursor = conn.cursor()

    hashed_pw = hash_password(user.password)

    cursor.execute(
        "INSERT INTO users(username, password) VALUES(?, ?)",
        (user.username, hashed_pw)
    )

    conn.commit()
    conn.close()

    return {"message": "User registered successfully"}

@app.post("/login")
def login(user: User):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT id, password FROM users WHERE username = ?",
        (user.username,)
    )

    result = cursor.fetchone()
    conn.close()

    if not result:
        raise HTTPException(status_code=400,detail="Invalid Credentials")
    
    user_id, hashed_password =result

    if not verify_password(user.password, hashed_password):
        raise HTTPException(status_code=400,detail="Invalid Credentials")
    
    token = create_access_token({"sub":user.username,"user_id":user_id})

    return{"access_token": token}



@app.get("/expenses")
def get_expenses(user = Depends(verify_token)):
    conn = sqlite3.connect("expense.db")
    cursor = conn.cursor()

    user_id = user["user_id"]

    cursor.execute(
        "SELECT id, amount, category FROM expenses WHERE user_id = ?",
        (user_id,)
    )

    rows = cursor.fetchall()

    conn.close()

    expenses = []

    for row in rows:
        expenses.append({
            "id": row[0],
            "amount": row[1],
            "category": row[2]
        })

    return expenses

@app.get("/expenses/{expense_id}")
def get_expense(expense_id:int):
    conn = sqlite3.connect("expense.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM expenses WHERE id = ?",(expense_id,))
    row = cursor.fetchone()

    conn.close()

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

    conn.close()
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
    total = cursor.fetchone()[0] or 0

    cursor.execute("SELECT category, sum(amount) FROM expenses GROUP BY category")
    rows = cursor.fetchall()
    
    categories = {row[0]: row[1] for row in rows }
    highest_category = max(categories, key=categories.get) if categories else None

    category_percentages = {}
    if total >0:
        for category, amount in categories.items():
            category_percentages[category] = round((amount/total)*100,2)

    cursor.execute("SELECT category, monthly_limit FROM budgets")
    budget_rows = cursor.fetchall()

    budget_limits = {row[0]: row[1] for row in budget_rows}

    budget_warnings = []

    for category, amount in categories.items():
        if category in budget_limits:
            if amount > budget_limits[category]:
                budget_warnings.append(
                    f"{category} exceeds budget by{amount - budget_limits[category]}"
                )


    risk_flags = []
    for category, percent in category_percentages.items():
        if percent >= 50:
            risk_flags.append(f"{category} exceeds 50% of total spending")
    if total == 0:
        risk_flags.append("No Spending Data available")

    summary_data ={
        "total":total,
        "categories":categories,
        "highest_category":highest_category,
        "percentage":category_percentages,
        "risk_flgas":risk_flags,
        "budget_warnings":budget_warnings
    }

    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        raise HTTPException(status_code=500,detail="OpenAI API KEY IS NOT CONFIGURED")
    
    try:
        insight = generate_insight(summary_data,api_key)
        return{"total_spending":total,
               "highest_category":highest_category,
               "category_breakdown":categories,
               "ai_insight":insight,
               "percentage":category_percentages,
               "budget_warnings":budget_warnings}
    
    except Exception as e:
        raise HTTPException(status_code=500,detail="AI genration failed{str(e)}")

   
@app.put("/expenses/{expense_id}")
def update_expense(expense_id:int, expense: Expense):
    conn = sqlite3.connect("expense.db") 
    cursor = conn.cursor()

    cursor.execute(
        "UPDATE expenses SET amount = ?, category = ? WHERE id =? ",
        (expense.amount, expense.category, expense_id)
    )

    conn.commit()
    updated_count = cursor.rowcount
    conn.close()

    if updated_count == 0:
        return{"error":"Expense Not found"}
    
    return{"Message": "Expense added succesfully"}


@app.delete("/expenses/{expense_id}")
def delete_expense(expense_id:int):
   conn = get_connection()
   cursor = conn.cursor()

   cursor.execute("DELETE FROM expenses WHERE id = ?",(expense_id,))
   conn.commit 

   deleted_count = cursor.rowcount
   conn.close()

   if deleted_count == 0:
       raise HTTPException(status_code = 404, detail = "Expense Not Found")
   
   return{"Message":"Expense Deleted Succesfully"}