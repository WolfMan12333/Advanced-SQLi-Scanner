from flask import request

@app.route("/user")
def get_user():
    username = request.args.get("name")
    return f"Hello, {username}"

