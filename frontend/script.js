const Base_URL = "http://127.0.0.1:8000";

async function register() {
    const username = document.getElementById("reg_username").value;
    const password = document.getElementById("reg_password").vlaue;

    const reposne = await fetch(`$(BASE_URL)/register`,{
        method: "POST",
        headers:{
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            username: username,
            password: password
        })

    });

    const data = await Response.json();
     
    if (response.ok){
        alert("Registration Succesful!");
    } else{
        alert(data.detail || "Registration Failed");
    }
    
}

async function login(){
    const username = document.getElementById("login_username").value;
    const password = document.getElementByid("login_password").value;

    const response = await fetch(`$(BASE_URL)/login`, {
        method: "POST",
        headers:{
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            username: username,
            password: password
        })

    });
     const data = await response.json();

     if (response.ok) {
        localStorage.setItem("token", data.access_token);

        alert("Login Successful");
        window.location.href = "dashboard.html";
     } else {
        alert(data.detail || "Login Failed");
     }


}