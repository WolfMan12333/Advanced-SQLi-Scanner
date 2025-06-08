from flask import request

@app.route("/login")
def login():
    token = request.args.get("token")
    query = f"SELECT * FROM sessions WHERE token = '{token}'"
    return db.execute(query)

