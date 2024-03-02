from flask import Flask, render_template, request, jsonify
import json

app = Flask(__name__)

@app.route('/')
def index():
    with open('data.json', 'r') as file:
        ipos = json.load(file)
    return render_template('index.html', ipos=ipos, users=[
        "puja", "benazir", "me", "Farheen",
        "Subbu", "n", "sagar", "papa", "ma",
        "hamza pop", "hamza", "sufi", "Mama"
    ])

@app.route('/get_ipo_details/<ipo_name>')
def get_ipo_details(ipo_name):
    with open('data.json', 'r') as file:
        ipos = json.load(file)
        selected_ipo = next((ipo for ipo in ipos if ipo["Company Name"] == ipo_name), None)
    return jsonify(selected_ipo)

@app.route('/save_transaction', methods=['POST'])
def save_transaction():
    data = request.json

    with open('transactions.json', 'r') as file:
        transactions = json.load(file)

    transactions.append(data)

    with open('transactions.json', 'w') as file:
        json.dump(transactions, file, indent=4)

    return jsonify(message="Transaction data saved successfully!")

if __name__ == '__main__':
    app.run(debug=True)
