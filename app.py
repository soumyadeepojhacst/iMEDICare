from flask import Flask, request, render_template
from flask_cors import CORS
import google.generativeai as genai
import os
from dotenv import load_dotenv

app = Flask(__name__, template_folder='templates')
CORS(app)

# Gemini API configuration
load_dotenv()  # load variables from .env file
API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")


def generate_suggestions(age, height, weight, symptoms_text, user_query):
    try:
        height_m = float(height) / 100.0
        bmi = float(weight) / (height_m ** 2)
        bmi_value = round(bmi, 2)
    except Exception:
        bmi_value = "Not Available"

    user_text = f"Age: {age}, Height: {height} cm, Weight: {weight} kg, BMI: {bmi_value}."
    if symptoms_text:
        user_text += f" Reported Symptoms: {symptoms_text}."
    if user_query:
        user_text += f" Additional question: {user_query}."

    prompt = f"""
    You are a professional healthcare assistant. Based on these patient details:

    {user_text}

    Instructions:
    - If the user asked a specific question (like "Can I take ice cream when I have a cough?"),
      answer that clearly at the top before giving other insights.

    Then give the response in this exact structure:

    1. Possible Conditions:
       - List 3-5 related possible conditions (if symptoms are provided).

    2. Tips and Precautions:
       - Provide 5-7 general health and lifestyle tips relevant to these symptoms and BMI.

    3. Important Note:
       - Give a personalized note suggesting which specialist doctor they should visit 
         (e.g., gynecologist for pregnancy, psychologist for depression, cardiologist for chest pain, etc.)
       - End with: "Consult a qualified doctor for proper diagnosis and treatment."

    Rules:
    - Use bullet points starting with "-" only.
    - Keep the language clear and simple.
    """

    try:
        response = model.generate_content(prompt)
        cleaned = response.text.replace('*', '-')
        if "Important Note" in cleaned and "3." not in cleaned:
            cleaned = cleaned.replace("Important Note", "3. Important Note")
        return cleaned
    except Exception as e:
        return f"Error from Gemini API: {str(e)}"


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/suggest", methods=["POST"])
def suggest():
    age = request.form.get("age")
    height = request.form.get("height")
    weight = request.form.get("weight")
    symptoms_text = request.form.get("symptoms", "")
    user_query = request.form.get("extraQuery", "")

    suggestions = generate_suggestions(age, height, weight, symptoms_text, user_query)

    return render_template("result.html", suggestions=suggestions)


if __name__ == "__main__":
    app.run(debug=True)
