from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy # 🟢 NEW: Database Import
from datetime import datetime           # 🟢 NEW: For timestamps
import pandas as pd
import pickle
import os

app = Flask(__name__)
CORS(app)

# 🟢 NEW: Database Configuration
# This tells Flask to create a file called 'fraud_database.db' in the current folder
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'fraud_database.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize the Database
db = SQLAlchemy(app)

# 🟢 NEW: Define the Database Table (Schema)
class TransactionHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    transaction_type = db.Column(db.String(50))
    amount = db.Column(db.Float)
    old_balance = db.Column(db.Float)
    time_hour = db.Column(db.Float)
    risk_result = db.Column(db.String(20))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow) # Automatically saves the exact date/time it was checked

# Load the Smarter AI and the Text Translator
model = pickle.load(open('fraud_model.pkl', 'rb'))
encoder = pickle.load(open('type_encoder.pkl', 'rb'))

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
        
    file = request.files['file']

    try:
        df = pd.read_csv(file, low_memory=False)
        df.columns = df.columns.str.lower()
        results = []
        db_records = [] # 🟢 NEW: List to hold records for the database

        for index, row in df.iterrows():
            try:
                amount = float(row['amount'])
                time = float(row['time']) 
                transaction_type = str(row['type']).upper()
                old_balance = float(row['oldbalanceorg']) 
                
                try:
                    type_encoded = encoder.transform([transaction_type])[0]
                except:
                    type_encoded = encoder.transform(['PAYMENT'])[0] 
                
                prediction = model.predict([[amount, time, type_encoded, old_balance]])
                pred_str = str(prediction[0])
                safe_prediction = 'Fraud' if ('-1' in pred_str) else 'Safe'

                # Save for the UI
                results.append({
                    "amount": amount, "time": time, "type": transaction_type,
                    "oldbalance": old_balance, "result": safe_prediction
                })

                # 🟢 NEW: Prepare the record for the Database
                new_record = TransactionHistory(
                    transaction_type=transaction_type,
                    amount=amount,
                    old_balance=old_balance,
                    time_hour=time,
                    risk_result=safe_prediction
                )
                db_records.append(new_record)
            
            except Exception as e:
                print(f"Row {index} skipped: Error - {e}")

        # 🟢 NEW: Save ALL processed rows to the database at once!
        if db_records:
            db.session.bulk_save_objects(db_records)
            db.session.commit()
            print(f"✅ Successfully saved {len(db_records)} records to the database!")

        display_results = results[:100] 
        return jsonify(display_results)

    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
@app.route('/predict', methods=['POST'])
def predict_single():
    data = request.get_json()
    if not data: return jsonify({'error': 'No data provided'}), 400

    try:
        amount = float(data.get('amount', 0))
        time = float(data.get('time', 0))
        transaction_type = data.get('type', 'PAYMENT')
        old_balance = float(data.get('oldbalance', 0))
        
        if time < 0 or time > 24: return jsonify({'error': 'Time must be between 0 and 24'}), 400
        if amount < 0 or old_balance < 0: return jsonify({'error': 'Amounts cannot be negative'}), 400
        
        try:
            type_encoded = encoder.transform([transaction_type])[0]
        except:
            type_encoded = encoder.transform(['PAYMENT'])[0]
            
        prediction = model.predict([[amount, time, type_encoded, old_balance]])
        
        pred_str = str(prediction[0])
        final_result = 'Fraud' if ('-1' in pred_str) else 'Safe'

        # 🟢 NEW: Save this single check to the database!
        new_transaction = TransactionHistory(
            transaction_type=transaction_type,
            amount=amount,
            old_balance=old_balance,
            time_hour=time,
            risk_result=final_result
        )
        db.session.add(new_transaction)
        db.session.commit()
        print(f"✅ Saved single transaction to DB: {transaction_type} | ₹{amount} -> {final_result}")

        return jsonify({'result': final_result})

    except Exception as e:
        print(f"Prediction error: {e}")
        return jsonify({'error': str(e)}), 500

# 🟢 NEW: Create the database file if it doesn't exist yet
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)