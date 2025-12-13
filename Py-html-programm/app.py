from flask import Flask, render_template, request, redirect, url_for, jsonify, session
import json
from random import randint, choice

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

    user_data = {
        "user_name": name,
        "key_word": password,
        "first_time": True
    }

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
        try:
            with open("users.json", 'r') as f:
                content = f.read().strip()
                users = json.loads(content) if content else []
        except (FileNotFoundError, json.JSONDecodeError):
            users = []

        for person in users:
            if person["user_name"] == name and person["key_word"] == password:
                session["user_name"] = name
                if person.get("first_time", True):
                    return redirect(url_for("first_pick"))
                else:
                    return redirect(url_for("game"))

        return render_template("login_page.html", out_put="This account doesn't exist")

    return render_template("login_page.html")

@app.route("/stats", methods=['POST', 'GET'])
def first_pick():
    if request.method == "POST":
        username = session.get("user_name")
        char_name = request.form.get("char_name")
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
                user.update({
                    "char_name": char_name,
                    "class": class_name,
                    "hp": hp,
                    "damage": damage,
                    "armor": armor,
                    "stamina": stamina,
                    "original_stamina": stamina,
                    "evade": evade,
                    "first_time": False
                })
                break

        with open("users.json", 'w') as f:
            json.dump(users, f)

        return redirect(url_for("game"))

    return render_template("stats.html")

@app.route("/game", methods=["GET", "POST"])
def game():
    if request.method == "POST":
        action = request.form.get("action")
        session["last_action"] = action
        return redirect(url_for("game"))
    else:
        action = session.pop("last_action", None)

    if "player_turn" not in session:
        session["player_turn"] = True
    if "battle_log" not in session:
        session["battle_log"] = []
    if "defending" not in session:
        session["defending"] = False
    if "dialogue_mode" not in session:
        session["dialogue_mode"] = True
    if "current_dialogue" not in session:
        session["current_dialogue"] = "intro"
    if "dialogue_index" not in session:
        session["dialogue_index"] = 0

    session.setdefault("is_defending", False)
    log = session["battle_log"]
    player_turn = session["player_turn"]
    dialogue_mode = session["dialogue_mode"]
    current_dialogue = session["current_dialogue"]
    dialogue_index = session["dialogue_index"]

    username = session.get("user_name")
    try:
        with open("users.json", "r") as f:
            users = json.loads(f.read().strip() or "[]")
    except:
        users = []

    user = next((u for u in users if u["user_name"] == username), None)
    if not user:
        return "No user found! Please log in first."

    user.setdefault("max_hp", user.get("hp", 100))
    user.setdefault("max_stamina", user.get("original_stamina", 100))
    user.setdefault("stamina", user.get("stamina", user["max_stamina"]))
    user.setdefault("defeated_enemies", [])

    all_enemies = [
        {"name": "Goblin", "hp": 100, "moves": {"slam": 10, "stab": 15}},
        {"name": "Orc", "hp": 150, "moves": {"smash": 15, "bash": 20}},
        {"name": "Troll", "hp": 300, "moves": {"club": 20, "stomp": 25}},
        {"name": "Skeleton Archer", "hp": 80, "moves": {"arrow shot": 10, "poison arrow": 12}},
        {"name": "Dark Mage", "hp": 120, "moves": {"fireball": 20, "dark bolt": 25}}
    ]

    if "enemies" not in session or session.get("reset_enemies", False):
        enemies = [e.copy() for e in all_enemies if e["name"] not in user["defeated_enemies"]]
        session["enemies"] = enemies
        session.pop("reset_enemies", None)
    else:
        enemies = session["enemies"]

    enemy = enemies[0] if enemies else None

    def battle(player, enemy_obj, action, player_turn_flag):# __________________________________
        msg = ""
        action_successful = True
        evade_index = randint((player["evade"] // 10), 10)

        if not enemy_obj:
            return player, enemy_obj, msg, False

        if player_turn_flag:
            if action == "attack":
                if player.get("stamina", 0) < 5:
                    msg = "You are too tired to attack!"
                    action_successful = False
                else:
                    damage = player.get("damage", 1)
                    enemy_obj["hp"] -= damage
                    player["stamina"] -= 5
                    msg = f"You attacked {enemy_obj['name']} for {damage} damage!"
                    session["is_defending"] = False
            elif action == "defend":
                session["is_defending"] = True
                msg = "You brace yourself and prepare to defend!"
            elif action == "rest":
                player["stamina"] = min(player.get("stamina", 0) + 10, player.get("max_stamina", player.get("original_stamina")))
                session["enemy_weakened"] = True
                msg = "You rested and recovered stamina! Enemy's next attack will be weaker."
        else:
            if session.get("enemy_acted", False):
                return player, enemy_obj, "", True

            move_name = choice(list(enemy_obj["moves"].keys()))
            move_damage = enemy_obj["moves"][move_name]
            move_damage -= (move_damage * (player["armor"] / 100))
            
            if evade_index == (player["evade"] // 10):
                msg = f"You evaded the {move_name} and got saved from {move_damage}!"
                move_damage = 0
            else:
                if session.get("is_defending", False):
                    move_damage //= 2

                if session.get("enemy_weakened", False):
                    move_damage = max(0, move_damage - 5)
                    session["enemy_weakened"] = False

                player["hp"] -= move_damage
                player["hp"] = max(player["hp"], 0)

                msg = f"{enemy_obj['name']} attacks you with {move_name} for {move_damage} damage!"
                session["enemy_acted"] = True
                session["is_defending"] = False

        if msg:
            log = session.get("battle_log", [])
            log.append(msg)
            session["battle_log"] = log

        return player, enemy_obj, msg, action_successful
    
    dialogues = {
        "intro": [
            "Welcome, hero! Your journey begins now.",
            "Be careful, enemies lurk in the shadows.",
            "Press 'Next' to continue..."
        ],
        "goblin": [
            "A sneaky goblin appears!",
            "It looks dangerous...",
            "Prepare yourself for battle!"
        ],
        "orc": [
            "An Orc blocks your path!",
            "Its club is huge!",
            "Get ready to fight!"
        ]
    }

    current_line = None
    if not action:
        action = request.args.get("action")
        delay_flag = request.args.get("delay") == "1"
    
    if dialogue_mode:
        current_line = dialogues.get(current_dialogue, [""])[dialogue_index]
        if action == "next_line":
            dialogue_index += 1
            if dialogue_index >= len(dialogues.get(current_dialogue, [])):
                session["dialogue_mode"] = False 
                dialogue_mode = False
                session["dialogue_index"] = 0
                session["current_dialogue"] = None
                session["player_turn"] = True 
                if enemies:
                    enemy = enemies[0]
                    log.append(f"{enemy['name']} appears!")
                    session["battle_log"] = log
            else:
                session["dialogue_index"] = dialogue_index
                current_line = dialogues[current_dialogue][dialogue_index]

    if "enemy_pending" not in session:
        session["enemy_pending"] = False
    if "enemy_acted" not in session:
        session["enemy_acted"] = False

    battle_msg = ""

    if action and session.get("player_turn", True) and enemy and not dialogue_mode:
        # Player acts
        user, enemy, battle_msg, action_successful = battle(user, enemy, action, player_turn_flag=True)
        session["player_turn"] = False
        session["enemy_acted"] = False

        # Enemy acts automatically
        if action_successful and enemy:
            user, enemy, enemy_msg, _ = battle(user, enemy, None, player_turn_flag=False)
            battle_msg += f" {enemy_msg}"
            session["player_turn"] = True
            session["enemy_acted"] = False
        for i, u in enumerate(users):
            if u["user_name"] == user["user_name"]:
                users[i] = user
        with open("users.json", "w") as f:
            json.dump(users, f)

        if enemy:
            enemies[0] = enemy
        session["enemies"] = enemies

    if enemy and enemy["hp"] <= 0:
        defeat_msg = f"You defeated {enemy['name']}!"
        log.append(defeat_msg)
        session["battle_log"] = log

        if enemy["name"] not in user["defeated_enemies"]:
            user["defeated_enemies"].append(enemy["name"])

        user["hp"] = user.get("max_hp", 100)
        user["stamina"] = user.get("original_stamina", 10)

        enemies.pop(0)
        session["enemies"] = enemies
        battle_msg = defeat_msg

        for i, u in enumerate(users):
            if u["user_name"] == user["user_name"]:
                users[i] = user
        with open("users.json", "w") as f:
            json.dump(users, f)

        if enemies:
            enemy = enemies[0]
            session["dialogue_mode"] = True
            session["current_dialogue"] = enemy["name"].lower()
            session["dialogue_index"] = 0
            session["player_turn"] = False
            current_line = dialogues.get(enemy["name"].lower(), [""])[0]
            battle_msg = f"You defeated the previous enemy! Next enemy approaches: {enemy['name']}!"
        else:
            enemy = None
            session["dialogue_mode"] = False
            session["player_turn"] = True
            current_line = None

    if user.get("hp", 0) <= 0:
        keys_to_remove = ["char_name", "class", "hp", "damage", "armor", "stamina", "evade", "defeated_enemies"]
        for key in keys_to_remove:
            user.pop(key, None)
        user["first_time"] = True
        session.pop("enemies", None)
        session.pop("battle_log", None)
        session["reset_enemies"] = True

        session["dialogue_mode"] = True
        session["current_dialogue"] = "intro"
        session["dialogue_index"] = 0

        for i, u in enumerate(users):
            if u["user_name"] == user["user_name"]:
                users[i] = user
        with open("users.json", "w") as f:
            json.dump(users, f)
        return redirect(url_for("first_pick"))

    return render_template(
        "game.html",
        hp=user.get("hp", 0),
        damage=user.get("damage", 0),
        armor=user.get("armor", 0),
        evade=user.get("evade", 0),
        stamina=user.get("stamina", 0),
        enemy_health=enemy["hp"] if enemy else None,
        enemy_name=enemy["name"] if enemy else None,
        battle_msg=battle_msg,
        battle_log=log,
        dialogue_mode=session["dialogue_mode"],
        current_line=current_line,
        player_turn=session.get("player_turn", True)
    )

if __name__ == "__main__":
    app.run(debug=True)