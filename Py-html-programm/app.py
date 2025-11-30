from flask import Flask, render_template, request
import json

app = Flask(__name__)

def character_limit(func):
    def wrapper(password):
        if len(password) < 3 or len(password) > 16:
            return "Password must be between 3 and 16 characters"
        return func(password)
    return wrapper

def check_digits(func):
    def wrapper(password):
        if password.isdigit():
            return "You have to use letters and special characters"
        if not any(char.isdigit() for char in password):
            return "You have to use numbers"
        return func(password)
    return wrapper

def check_upper(func):
    def wrapper(password):
        if not isinstance(password, str):
            return "Password invalid"
        if not any(char.isupper() for char in password):
            return "You have to have at least one uppercase letter"
        return func(password)
    return wrapper

@check_upper
@check_digits
@character_limit
def password_checker(password: str) -> str:
    return f"Good, your password is {password} and it's good to go"

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/signup", methods=["POST"])
def signup():
    name = request.form.get("name")
    password = request.form.get("password")

    user_data = {"user_name": name, "key_word": password}

    try:
        with open("Py-html-programm/users.json", 'r') as f:
            content = f.read().strip()
            users = json.loads(content) if content else []
    except (FileNotFoundError, json.JSONDecodeError):
        users = []

    for person in users:
        if name == person["user_name"]:
            return render_template("index.html", pass_result='', name_result="Username already taken")

    users.append(user_data)
    with open("Py-html-programm/users.json", 'w') as f:
        json.dump(users, f)

    pass_result = password_checker(password)
    return render_template("index.html", pass_result=pass_result)

@app.route("/login", methods=["POST", "GET"])
def check_login():
    if request.method == "POST":
        name = request.form.get("name")
        password = request.form.get("password")
        user_data = {"user_name": name, "key_word": password}

        try:
            with open("Py-html-programm/users.json", 'r') as f:
                content = f.read().strip()
                users = json.loads(content) if content else []
        except (FileNotFoundError, json.JSONDecodeError):
            users = []

        for person in users:
            if user_data["user_name"] == person["user_name"] and user_data["key_word"] == person["key_word"]:
                return render_template("login_page.html", out_put=f"Welcome back, {name}!")

        return render_template("login_page.html", out_put="This account doesn't exist")
    

    return render_template("login_page.html")

if __name__ == "__main__":
    app.run(debug=True)