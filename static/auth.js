// login 

async function login() {
    let name = document.getElementById("loginname").value;
    let password = document.getElementById("loginpassword").value;

    let res = await fetch("/login", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({name, password})
    }) 
    let data = await res.json()

    if (res.ok){
        window.location.href = "/feed"
    } else {
        document.getElementById("login-message").textContent = data.error;
    }
}

// #signup

async function signup() {
    let name = document.getElementById("signupname").value;
    let password = document.getElementById("signuppassword").value;

    let res = await fetch("/signup", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({name, password})
    });
    let data = await res.json();

    if (res.ok) {
        window.location.href = "/feed";
    } else {
        document.getElementById("signup-message").textContent = data.error;
    }
}