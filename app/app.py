from flask import Flask, request, jsonify, render_template_string
import psycopg2
import os
import time

app = Flask(__name__)
conn = None
cur = None

def init_db():
    global conn, cur
    while True:
        try:
            conn = psycopg2.connect(
                dbname=os.getenv("POSTGRES_DB"),
                user=os.getenv("POSTGRES_USER"),
                password=os.getenv("POSTGRES_PASSWORD"),
                host=os.getenv("POSTGRES_HOST"),
                port=os.getenv("POSTGRES_PORT", 5432)
            )
            cur = conn.cursor()
            cur.execute("CREATE TABLE IF NOT EXISTS notes (id SERIAL PRIMARY KEY, content TEXT);")
            conn.commit()
            break
        except Exception as e:
            print("Waiting for database...")
            time.sleep(2)

# 🛑 Skip DB connection during testing (e.g., in CI)
if os.getenv("FLASK_ENV") != "testing":
    init_db()

@app.route("/add", methods=["POST"])
def add_note():
    note = request.json.get("note")
    cur.execute("INSERT INTO notes (content) VALUES (%s);", (note,))
    conn.commit()
    return jsonify({"status": "ok"})

@app.route("/notes", methods=["GET"])
def get_notes():
    cur.execute("SELECT * FROM notes;")
    notes = cur.fetchall()
    return jsonify(notes)

@app.route("/form", methods=["GET", "POST"])
def form():
    message = ""
    if request.method == "POST":
        note = request.form.get("note")
        if note:
            cur.execute("INSERT INTO notes (content) VALUES (%s);", (note,))
            conn.commit()
            message = "Note added successfully!"
    return render_template_string("""
        <html>
            <head><title>Note Form</title></head>
            <body>
                <h2>Add a Note</h2>
                <form method="POST">
                    <input type="text" name="note" placeholder="Enter your note" required>
                    <button type="submit">Submit</button>
                </form>
                <p>{{ message }}</p>
                <br>
                <a href="/notes">View Notes (JSON)</a>
            </body>
        </html>
    """, message=message)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5050)