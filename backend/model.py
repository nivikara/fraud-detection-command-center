import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import LabelEncoder
import pickle

print("Reading only100.csv...")
# 1. Load your actual dataset
data = pd.read_csv('only100.csv')

# 2. Initialize our "Text to Math" Translator
encoder = LabelEncoder()

# 3. Translate the 'type' column (PAYMENT, TRANSFER, etc.) into numbers
data['type_encoded'] = encoder.fit_transform(data['type'])

# 4. Select our new "Context-Aware" features
features = ['amount', 'time', 'type_encoded', 'oldbalanceOrg']
X = data[features]

# 5. Train the Smarter AI
print("Training the context-aware AI...")
model = IsolationForest(contamination=0.05, random_state=42)
model.fit(X)

# 6. Save BOTH the Model and the Translator
with open('fraud_model.pkl', 'wb') as f:
    pickle.dump(model, f)
    
with open('type_encoder.pkl', 'wb') as f:
    pickle.dump(encoder, f)

print("SUCCESS: fraud_model.pkl and type_encoder.pkl have been created!")