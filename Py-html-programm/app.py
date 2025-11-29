from flask import Flask, render_template

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
    name = "Boryslav"
    return render_template("index.html", name=name)



if __name__ == "__main__":
    app.run(debug=True)
