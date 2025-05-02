from fastapi import FastAPI
from pydantic import BaseModel
import requests
import json

app = FastAPI()

with open("questions.json", "r", encoding="utf-8") as f:
    questions_by_age = json.load(f)

AZURE_OPENAI_ENDPOINT = "https://chatahmedfarouk.cognitiveservices.azure.com/openai/deployments/gpt-35-turbo-2/chat/completions?api-version=2025-01-01-preview"
AZURE_API_KEY = "Da3NoVCmbrOuEP2FyxS4UjAlDjI2CTmqFSZSbHmzZG8kN9OqxLBxJQQJ99BCAC5T7U2XJ3w3AAAAACOGVFOy"

session_answers = {}

class ChatRequest(BaseModel):
    age: int
    language: str  
    current_question: str = ""
    answer: str = ""  

def get_age_group(age):
    if age <= 3:
        return "0-3"
    elif age <= 6:
        return "4-6"
    elif age <= 9:
        return "7-9"
    elif age <= 12:
        return "10-12"
    elif age <= 15:
        return "13-15"
    elif age <= 18:
        return "16-18"
    elif age <= 21:
        return "19-21"
    else:
        return "22-24"

def call_azure_openai(messages, language):
    headers = {"Content-Type": "application/json", "api-key": AZURE_API_KEY}
    system_prompt = "You are a smart assistant giving advice to mothers." if language == "en" else "أنت مساعد ذكي تعطي نصائح للأمهات."
    body = {
        "messages": [{"role": "system", "content": system_prompt}] + messages,
        "max_tokens": 200,
        "temperature": 0.7
    }
    response = requests.post(AZURE_OPENAI_ENDPOINT, headers=headers, json=body)
    response.raise_for_status()
    return response.json()["choices"][0]["message"]["content"]

def check_answer_relevance(question, answer, language):
    headers = {"Content-Type": "application/json", "api-key": AZURE_API_KEY}
    prompt = (
        f"Question: {question}\n"
        f"User Answer: {answer}\n\n"
        "Instructions:\n"
        "- Deeply understand the question's intent and the user's answer.\n"
        "- Normalize typos, informal language, slang, and infer the intended meaning.\n"
        "- VERY IMPORTANT: Even if the answer is extremely short (one or two words), if it carries a meaning that relates to the question's topic, classify it as **relevant**.\n"
        "- ONLY classify as **not relevant** if the answer has no semantic connection to the question.\n"
        "- Reply with exactly one word: relevant or not relevant (lowercase). Do not explain."
    )
    body = {
        "messages": [{"role": "system", "content": "Act as a helpful assistant that determines if an answer is relevant to a given question."},
                     {"role": "user", "content": prompt}],
        "max_tokens": 10,
        "temperature": 0
    }
    response = requests.post(AZURE_OPENAI_ENDPOINT, headers=headers, json=body)
    response.raise_for_status()
    result = response.json()["choices"][0]["message"]["content"].strip().lower()

    # هنا التشدد
    if result == "relevant":
        return True
    elif result == "not relevant":
        return False
    else:
        return False


@app.post("/chat")
async def chat(req: ChatRequest):
    if req.age < 0 or req.age > 24:
        return {"error": "Age must be between 0 and 24 months."}

    if req.language not in ["ar", "en"]:
        return {"error": "Language must be 'ar' or 'en'."}

    age_group = get_age_group(req.age)
    language = req.language
    questions = questions_by_age.get(age_group, {}).get(language, [])

    if not questions:
        return {"message": "No questions available for this age."}

    user_id = f"user_{req.age}_{language}"    
    if user_id not in session_answers:
        session_answers[user_id] = {}

    # بداية المحادثة
    if not req.current_question:
        return {"question": questions[0]}

    if req.current_question not in questions:
        return {"error": "Unknown current question."}

    answer = req.answer.strip()
    if not answer:
        return {"error": "Please provide an answer for the question."}

    try:
        is_relevant = check_answer_relevance(req.current_question, answer, language)
        if not is_relevant:
            return {"message": "Please provide an answer relevant to the question."}
    except Exception as e:
        return {"error": f"Error checking relevance: {str(e)}"}

    session_answers[user_id][req.current_question] = answer

    curr_index = questions.index(req.current_question)
    if curr_index + 1 < len(questions):
        next_question = questions[curr_index + 1]
    else:
        next_question = "All questions are done. Thank you!"

    messages = []
    for q, a in session_answers[user_id].items():
        messages.append({"role": "user", "content": f"Question: {q}, Answer: {a}"})
    messages.append({"role": "user", "content": "What is your advice for the mother based on this information?"})

    try:
        advice = call_azure_openai(messages, language)
    except Exception as e:
        advice = f"Error getting advice: {str(e)}"

    return {
        "advice": advice,
        "next_question": next_question
    }

@app.get("/")
async def root():
    return {"message": "Welcome to the Mother Advice Chatbot 🎉"}
