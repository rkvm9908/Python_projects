# src/app.py

from flask import Flask, render_template, request, jsonify
import joblib
import os
import time 
from preprocess import clean_text 
from genai_model import analyze_offer_with_genai

APP = Flask(__name__, template_folder="templates", static_folder="static")
MODEL_PATH = "src/model/model_v2.joblib" 
VEC_PATH = "src/model/vectorizer_v2.joblib" 

try:
    if not os.path.exists(MODEL_PATH) or not os.path.exists(VEC_PATH):
        raise FileNotFoundError(f"Model or vectorizer not found. Run training script first. Expected: {MODEL_PATH}, {VEC_PATH}")
    
    MODEL = joblib.load(MODEL_PATH)
    VEC = joblib.load(VEC_PATH)
    print("✅ Model and Vectorizer loaded successfully.")

except FileNotFoundError as e:
    print(f"❌ ERROR: {e}")
    MODEL = None
    VEC = None

def get_offer_type(text):
    """
    Analyzes text to classify the offer type (Scholarship or Job).
    """
    text_lower = text.lower()
    scholarship_keywords = ["scholarship", "fellowship", "tuition", "grant", "financial aid", "stipend", "admission"]
    job_keywords = ["job", "position", "internship", "hiring", "vacancy", "role", "salary", "employment"]

    if any(w in text_lower for w in scholarship_keywords):
        if any(w in text_lower for w in job_keywords):
            return "Mixed Offer"
        return "Scholarship Offer"

    elif any(w in text_lower for w in job_keywords):
        return "Job Offer"
    else:
        return "General/Unknown Offer"

def predict_offer(text):
    """Processes text and returns prediction results."""
    start_time = time.time()
    if MODEL is None or VEC is None:
        return {
            'label': 'Model Error',
            'prob_fake': 0.5,
            'genai_explanation': None,
            'time': 0.001
        }
    try:
        cleaned_text = clean_text(text)
        features = VEC.transform([cleaned_text])
        prob_array = MODEL.predict_proba(features)
        prob_fake = prob_array[0][1]
        if prob_fake >= 0.5:
            label = "Fake"
        else:
            label = "Genuine"
            
        genai_explanation = analyze_offer_with_genai(text)
            
        end_time = time.time()
        return {
            'label': label,
            'prob_fake': float(prob_fake),
            'genai_explanation': genai_explanation,
            'time': end_time - start_time
        }
    except Exception as e:
        print(f"Prediction failed: {e}")
        return {
            'label': 'Internal Error',
            'prob_fake': 0.5,
            'genai_explanation': None,
            'time': time.time() - start_time
        }

# --- 4. Web Routes ---

@APP.route("/", methods=["GET"])
def index():
    return render_template("index.html")


@APP.route('/predict', methods=['POST'])
def web_predict():
    """Handles web form submission and displays results."""
    
    text = request.form.get('text', '')
    
    if not text:
        return render_template('index.html', error="Please paste text for analysis.")
    results = predict_offer(text)
    offer_type = get_offer_type(text)
    return render_template('result.html', 
                        text=text,
                        label=results['label'], 
                        prob=results['prob_fake'],
                        time_taken=results['time'],
                        genai_explanation=results.get('genai_explanation'),
                        offer_type=offer_type)
    

@APP.route("/api/predict", methods=["POST"])
def api_predict():
    """Handles API requests and returns JSON response."""
    
    try:
        data = request.get_json(force=True)
        text = data.get("text", "")
    except Exception:
        return jsonify({'error': 'Invalid JSON format or missing "text" field.'}), 400

    if not text:
        return jsonify({'error': 'Missing "text" field in the request body.'}), 400
        
    # Use the core predict function for consistency
    results = predict_offer(text) 
    
    return jsonify({
        "label": results['label'], 
        "probability_fake": results['prob_fake'],
        "offer_type": get_offer_type(text),
        "genai_explanation": results.get('genai_explanation'),
        "time_ms": results['time'] * 1000 
    })

# --- 6. Run Application ---
if __name__ == "__main__":
    APP.run(debug=True, host="0.0.0.0", port=5000)