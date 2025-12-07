from flask import Flask, render_template, request, redirect, url_for, jsonify, session
import json


app = Flask(__name__)
app.secret_key = "Timberlake"

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


    user_data = {"user_name": name, "key_word": password, "first_time": True}


    try:
        with open("users.json", 'r') as f:
            content = f.read().strip()
            users = json.loads(content) if content else []
    except (FileNotFoundError, json.JSONDecodeError):
        users = []


    for person in users:
        if name == person["user_name"]:
            return render_template("index.html", pass_result='', name_result="Username already taken")


    pass_result = password_checker(password)


    users.append(user_data)
    with open("users.json", 'w') as f:
        json.dump(users, f)

    session["user_name"] = name

    return render_template("index.html", pass_result=pass_result)


@app.route("/login", methods=["POST", "GET"])
def check_login():
    if request.method == "POST":
        name = request.form.get("name")
        password = request.form.get("password")
        user_data = {"user_name": name, "key_word": password}


        try:
            with open("users.json", 'r') as f:
                content = f.read().strip()
                users = json.loads(content) if content else []
        except (FileNotFoundError, json.JSONDecodeError):
            users = []


        for person in users:
            if user_data["user_name"] == person["user_name"] and user_data["key_word"] == person["key_word"]:
                if person["first_time"]:
                    person["first_time"] = True
                    
                    with open("users.json", "w") as f:
                        json.dump(users, f)
                    
                    session["user_name"] = name

                    return redirect(url_for("first_pick"))

                return render_template("login_page.html", out_put=f"Welcome back, {name}!")


        return render_template("login_page.html", out_put="This account doesn't exist")
   


    return render_template("login_page.html")

@app.route("/stats", methods=['POST', 'GET'])
def first_pick():
    if request.method == "POST":
        char_name = request.form.get("char_name")
        username = session.get("user_name")
        class_name = request.form.get("class")
        hp = int(request.form.get("hp"))
        damage = int(request.form.get("damage"))
        armor = int(request.form.get("armor"))
        stamina = int(request.form.get("stamina"))
        evade = int(request.form.get("evade"))

        try:
            with open("users.json", 'r') as f:
                    content = f.read().strip()
                    users = json.loads(content) if content else []
        except (FileNotFoundError, json.JSONDecodeError):
                users = []
        
        for user in users:
            if user["user_name"] == username:
                user["char_name"] = char_name
                user["class"] = class_name
                user["hp"] = hp
                user["damage"] = damage
                user["armor"] = armor
                user["stamina"] = stamina
                user["evade"] = evade
                break
            
        with open("users.json", 'w') as f:
            json.dump(users, f)
        
        return render_template("stats.html")
    
    return render_template("stats.html")

if __name__ == "__main__":
    app.run(debug=True)
