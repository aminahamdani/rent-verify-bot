import sqlite3
from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse

app = Flask(__name__)

# --- Database Setup ---
def init_db():
    conn = sqlite3.connect('rent_data.db')
    cursor = conn.cursor()
    # Create the table if it doesn't exist
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS payments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            phone_number TEXT,
            status TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

# Initialize the DB when the script starts
init_db()

# --- The Routes ---

@app.route('/sms/', methods=['POST'])
def sms_reply():
    # 1. Get the incoming text
    incoming_msg = request.form.get('Body', '').strip()
    sender_phone = request.form.get('From', '')

    # 2. Prepare the response
    resp = MessagingResponse()

    # 3. Connect to DB to save the result
    conn = sqlite3.connect('rent_data.db')
    cursor = conn.cursor()

    # 4. Check logic (YES or NO)
    if incoming_msg.upper() == 'YES':
        cursor.execute("INSERT INTO payments (phone_number, status) VALUES (?, ?)", (sender_phone, 'PAID'))
        resp.message('Thank you! Payment verified. Saved to database.')
    elif incoming_msg.upper() == 'NO':
        cursor.execute("INSERT INTO payments (phone_number, status) VALUES (?, ?)", (sender_phone, 'NOT_PAID'))
        resp.message('Alert: Non-payment recorded.')
    else:
        resp.message('Please reply with YES or NO.')

    # 5. Save and Close DB
    conn.commit()
    conn.close()

    return str(resp)

@app.route('/dashboard')
def dashboard():
    # Connect to DB to read data
    conn = sqlite3.connect('rent_data.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM payments ORDER BY id DESC")
    rows = cursor.fetchall()
    conn.close()

    # Simple HTML to show the list
    html = "<h1>Rent Payment Dashboard</h1><table border='1'><tr><th>ID</th><th>Phone</th><th>Status</th><th>Time</th></tr>"
    for row in rows:
        html += f"<tr><td>{row[0]}</td><td>{row[1]}</td><td>{row[2]}</td><td>{row[3]}</td></tr>"
    html += "</table>"
    
    return html

if __name__ == '__main__':
    app.run(debug=True)