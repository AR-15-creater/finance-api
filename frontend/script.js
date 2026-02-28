const BASE_URL = "http://127.0.0.1:8000";

async function loadExpenses() {
    const token = localStorage.getItem("token");

    const response = await fetch(`${BASE_URL}/expenses`, {
        headers: {
            "Authorization": `Bearer ${token}`
        }
    });

    const expenses = await response.json();

    const list = document.getElementById("expenseList");
    list.innerHTML = "";

    expenses.forEach(exp => {
        const li = document.createElement("li");
        li.innerText = `${exp.amount} - ${exp.category}`;
        list.appendChild(li);
    });
}

async function addExpense() {
    console.log("Button clicked");

    const amount = document.getElementById("amount").value;
    const category = document.getElementById("category").value;
    const token = localStorage.getItem("token");

    const response = await fetch(`${BASE_URL}/expenses`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "Authorization": `Bearer ${token}`
        },
        body: JSON.stringify({
            amount: amount,
            category: category
        })
    });

    console.log("Response status:", response.status);

    await loadExpenses();
}

loadExpenses();