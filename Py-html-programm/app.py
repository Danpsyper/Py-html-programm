from flask import Flask, render_template, request
import json

app = Flask(__name__)

def charachter_limit(func):
    def wrapper(password):
        if len(password) < 3 or len(password) > 16:
            return "There has to be at least 3 or not more than 16 charachters"
        else:
            return func(password)
    return wrapper

def check_digits(func):
    def wrapper(password):
        if password.isdigit():
            return "You have to use letters and special charachters"
        if not any(char.isdigit() for char in password):
            return "You have to use numbers"
        return func(password)
    return wrapper

def check_upper(func):
    def wrapper(password):
        if  not any(char.isupper() for char in password):
            return "You have to have at least one upper case letter"
        else: 
            return func(password)
    return wrapper

@check_upper
@check_digits
@charachter_limit
def password_cheker(password: str) -> str:
    return f"Good, your password is {password} and it's good to go"

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/check", methods=["POST"])
def check():
    password = request.form.get("password")
    name = request.form.get("name")
    user_data = {"user_name": name, "key_word": password}
    
    try:
        with open("users.json", 'r') as f:
            content = f.read().strip()
            users = json.loads(content) if content else []
    except (FileNotFoundError, json.JSONDecodeError):
        users = []
    
    for person in users:
        if user_data["user_name"] == person["user_name"]:
            return render_template("index.html", pass_result=' ', name_result="Username already taken") 
    
    users.append(user_data)
    
    with open("users.json", 'w') as f:
        json.dump(users, f)
    
    pass_result = password_cheker(password)
    return render_template("index.html", pass_result=pass_result)

if __name__ == "__main__":
    app.run(debug=True)
