import difflib
import spacy
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

# === Load lightweight NLP ===
nlp = spacy.blank("en")
if "sentencizer" not in nlp.pipe_names:
    nlp.add_pipe("sentencizer")

# === Knowledge Base (your existing one) ===
KNOWLEDGE_BASE = {
    "common_cold": {
        "title": "Common Cold",
        "info": "A viral infection of the upper respiratory tract, mainly caused by rhinoviruses. It leads to mild symptoms like runny nose, sore throat, and cough.",
        "prevention": "Frequent handwashing, avoid close contact, maintain hygiene.",
        "care": "Rest, fluids, paracetamol/ibuprofen, decongestants. No antibiotics (viral)."
    },
    "influenza": {
        "title": "Influenza (Flu)",
        "info": "A contagious respiratory illness caused by influenza viruses. It can cause mild to severe illness and may lead to hospitalization.",
        "prevention": "Annual flu vaccination, hygiene, avoid close contact with infected people.",
        "care": "Antivirals if started early, fluids, rest, supportive care."
    },
    "covid_19": {
        "title": "COVID-19",
        "info": "A respiratory disease caused by SARS-CoV-2. Symptoms range from mild fever and cough to severe pneumonia and respiratory failure.",
        "prevention": "Vaccination, mask-wearing, good ventilation, testing, and isolation.",
        "care": "Supportive care, antivirals for high-risk cases, oxygen therapy if severe."
    },
    "tuberculosis": {
        "title": "Tuberculosis (TB)",
        "info": "A bacterial infection caused by Mycobacterium tuberculosis, usually affecting the lungs with symptoms like chronic cough, fever, and weight loss.",
        "prevention": "BCG vaccine, early detection, proper ventilation, avoid close contact with TB patients.",
        "care": "Long-term antibiotics (6+ months of multiple drugs)."
    },
    "pneumonia": {
        "title": "Pneumonia",
        "info": "Infection that inflames the air sacs in the lungs, which may fill with fluid. Caused by bacteria, viruses, or fungi.",
        "prevention": "Vaccines (pneumococcal, influenza), hygiene, avoid smoking.",
        "care": "Antibiotics if bacterial, antivirals if viral, oxygen and fluids if severe."
    },
    "bronchitis": {
        "title": "Bronchitis",
        "info": "Inflammation of the bronchial tubes, often following a cold. Can be acute (short-term) or chronic.",
        "prevention": "Avoid smoking, flu vaccine, maintain hygiene.",
        "care": "Rest, fluids, bronchodilators; antibiotics only if bacterial."
    },
    "asthma": {
        "title": "Asthma",
        "info": "A chronic lung condition where the airways narrow and swell, causing difficulty in breathing.",
        "prevention": "Avoid triggers such as smoke, dust, and allergens.",
        "care": "Inhaled corticosteroids, bronchodilators, lifestyle adjustments."
    },
    "diabetes_type1": {
        "title": "Diabetes Type 1",
        "info": "An autoimmune condition where the body stops producing insulin, leading to high blood sugar.",
        "prevention": "No known prevention (autoimmune condition).",
        "care": "Insulin therapy, blood sugar monitoring, balanced diet."
    },
    "diabetes_type2": {
        "title": "Diabetes Type 2",
        "info": "A chronic condition where the body becomes resistant to insulin or doesn't produce enough insulin.",
        "prevention": "Healthy diet, regular exercise, weight management.",
        "care": "Lifestyle changes, oral medications, insulin if needed."
    },
    "hypertension": {
        "title": "Hypertension (High Blood Pressure)",
        "info": "A condition where the force of the blood against artery walls is consistently too high.",
        "prevention": "Healthy diet, reduce salt, regular exercise, avoid stress.",
        "care": "Antihypertensive medications, lifestyle modifications."
    },
    "stroke": {
        "title": "Stroke",
        "info": "Occurs when blood supply to part of the brain is interrupted or reduced, depriving brain tissue of oxygen.",
        "prevention": "Control blood pressure, healthy diet, no smoking.",
        "care": "Emergency medical care, clot-busting drugs, rehabilitation."
    },
    "heart_attack": {
        "title": "Heart Attack",
        "info": "Occurs when blood flow to part of the heart is blocked, causing damage to heart muscle.",
        "prevention": "Healthy lifestyle, avoid smoking, manage cholesterol.",
        "care": "Immediate medical attention, aspirin, angioplasty, long-term medications."
    },
    "obesity": {
        "title": "Obesity",
        "info": "Excessive fat accumulation that increases the risk of many diseases like diabetes and heart disease.",
        "prevention": "Balanced diet, regular exercise, avoid processed foods.",
        "care": "Lifestyle changes, counseling, medications or surgery if needed."
    },
    "anemia": {
        "title": "Anemia",
        "info": "Condition where the body lacks enough healthy red blood cells to carry oxygen effectively.",
        "prevention": "Iron-rich diet, treat underlying causes, supplements if needed.",
        "care": "Iron supplements, blood transfusions in severe cases."
    },
    "malaria": {
        "title": "Malaria",
        "info": "A mosquito-borne infectious disease caused by Plasmodium parasites.",
        "prevention": "Mosquito nets, repellents, eliminate stagnant water.",
        "care": "Antimalarial drugs (artemisinin-based therapy)."
    },
    "dengue": {
        "title": "Dengue",
        "info": "A mosquito-borne viral infection causing high fever, rash, and muscle pain.",
        "prevention": "Mosquito control, protective clothing, repellents.",
        "care": "Supportive treatment: fluids, rest, acetaminophen for fever (no aspirin)."
    },
    "typhoid": {
        "title": "Typhoid Fever",
        "info": "Bacterial infection caused by Salmonella typhi, spread through contaminated food or water.",
        "prevention": "Safe drinking water, proper sanitation, vaccination.",
        "care": "Antibiotics, rehydration, balanced nutrition."
    },
    "cholera": {
        "title": "Cholera",
        "info": "A bacterial disease causing severe diarrhea and dehydration, usually spread in contaminated water.",
        "prevention": "Safe water, sanitation, vaccination.",
        "care": "Oral rehydration solution (ORS), IV fluids, antibiotics if severe."
    },
    "hepatitis_a": {
        "title": "Hepatitis A",
        "info": "A viral infection of the liver, usually spread by contaminated food and water.",
        "prevention": "Hepatitis A vaccination, good sanitation.",
        "care": "Rest, hydration, supportive care."
    },
    "hepatitis_b": {
        "title": "Hepatitis B",
        "info": "A serious liver infection caused by the hepatitis B virus, spread via blood or body fluids.",
        "prevention": "Hepatitis B vaccination, safe sex, avoid sharing needles.",
        "care": "Antiviral medications, liver monitoring."
    },
    "hiv_aids": {
        "title": "HIV/AIDS",
        "info": "A viral infection that attacks the immune system, making the body vulnerable to infections.",
        "prevention": "Safe sex, avoid sharing needles, HIV screening.",
        "care": "Antiretroviral therapy (ART), lifelong treatment."
    },
    "measles": {
        "title": "Measles",
        "info": "A highly contagious viral disease causing fever, cough, rash, and possible complications.",
        "prevention": "MMR vaccination.",
        "care": "Supportive care, vitamin A supplements."
    },
    "mumps": {
        "title": "Mumps",
        "info": "Viral infection that causes swelling of the salivary glands, fever, and muscle aches.",
        "prevention": "MMR vaccination.",
        "care": "Supportive care: rest, fluids, pain relief."
    },
    "rubella": {
        "title": "Rubella (German Measles)",
        "info": "A mild viral infection that causes rash and fever but dangerous during pregnancy.",
        "prevention": "MMR vaccination.",
        "care": "Supportive care, rest, fluids."
    },
    "polio": {
        "title": "Polio",
        "info": "A viral disease that can cause paralysis, sometimes permanent.",
        "prevention": "Polio vaccination.",
        "care": "Supportive care, physical therapy. No cure."
    },
    "tetanus": {
        "title": "Tetanus",
        "info": "Bacterial infection that causes painful muscle stiffness, often from contaminated wounds.",
        "prevention": "Tetanus vaccination, proper wound care.",
        "care": "Antitoxin, antibiotics, muscle relaxants."
    },
    "rabies": {
        "title": "Rabies",
        "info": "Deadly viral infection transmitted via bites or saliva from infected animals.",
        "prevention": "Rabies vaccination (post-exposure and pre-exposure), avoid stray animals.",
        "care": "Post-exposure prophylaxis (PEP). No cure once symptoms appear."
    },
    "leprosy": {
        "title": "Leprosy",
        "info": "A chronic infectious disease caused by Mycobacterium leprae, affecting skin, nerves, and mucous membranes.",
        "prevention": "Early diagnosis and treatment to prevent spread.",
        "care": "Multi-drug therapy (MDT)."
    },
    "plague": {
        "title": "Plague",
        "info": "Serious bacterial infection transmitted by fleas on rodents. Can be bubonic, septicemic, or pneumonic.",
        "prevention": "Rodent control, sanitation, avoid flea bites.",
        "care": "Antibiotics if treated early."
    },
    "ebola": {
        "title": "Ebola Virus Disease",
        "info": "A severe and often fatal illness in humans caused by the Ebola virus.",
        "prevention": "Avoid contact with infected people/animals, protective gear, safe burial practices.",
        "care": "Supportive care, fluids, experimental antiviral therapies."
    },
    "zika": {
        "title": "Zika Virus",
        "info": "Mosquito-borne viral infection linked to birth defects in newborns.",
        "prevention": "Mosquito control, protective clothing, repellents.",
        "care": "Supportive care, rest, hydration."
    },
    "hantavirus": {
        "title": "Hantavirus",
        "info": "A rare but severe respiratory disease transmitted by infected rodents. Can progress rapidly to respiratory failure.",
        "prevention": "Avoid contact with rodents and nesting areas. Use caution when cleaning barns/sheds.",
        "care": "No specific treatment. Supportive hospital care for breathing difficulties."
    },
    "yellow_fever": {
        "title": "Yellow Fever",
        "info": "Mosquito-borne viral disease causing fever, jaundice, and bleeding.",
        "prevention": "Yellow fever vaccination, mosquito control.",
        "care": "Supportive care: fluids, rest, pain management."
    },
    "chikungunya": {
        "title": "Chikungunya",
        "info": "Mosquito-borne viral disease causing severe joint pain and fever.",
        "prevention": "Mosquito control, repellents, protective clothing.",
        "care": "Supportive treatment, pain relievers, fluids."
    },
    "ringworm": {
        "title": "Ringworm",
        "info": "A contagious fungal infection of the skin causing circular rashes.",
        "prevention": "Good hygiene, avoid sharing towels/clothing.",
        "care": "Topical antifungal creams, oral antifungals if severe."
    },
    "athletes_foot": {
        "title": "Athlete’s Foot",
        "info": "Fungal infection that usually begins between the toes, causing itching and scaling.",
        "prevention": "Keep feet dry, avoid tight shoes, wear clean socks.",
        "care": "Topical antifungal creams, powders."
    },
    "cancer": {
        "title": "Cancer",
        "info": "A group of diseases involving abnormal cell growth with potential to invade or spread.",
        "prevention": "Healthy lifestyle, regular screening, avoid tobacco and excessive alcohol.",
        "care": "Surgery, chemotherapy, radiation, immunotherapy depending on type."
    },
    "alzheimer": {
        "title": "Alzheimer’s Disease",
        "info": "A progressive brain disorder leading to memory loss and cognitive decline.",
        "prevention": "Healthy lifestyle, brain activity, control risk factors like hypertension.",
        "care": "No cure. Symptom management with medications and support."
    },
    "parkinsons": {
        "title": "Parkinson’s Disease",
        "info": "A progressive nervous system disorder affecting movement.",
        "prevention": "No known prevention. Healthy lifestyle may help reduce risk.",
        "care": "Medications (levodopa), physical therapy, surgery in some cases."
    },
    "epilepsy": {
        "title": "Epilepsy",
        "info": "A neurological disorder marked by recurrent seizures.",
        "prevention": "Prevent head injuries, healthy lifestyle.",
        "care": "Anti-seizure medications, sometimes surgery."
    },
    "depression": {
        "title": "Depression",
        "info": "A mental health disorder characterized by persistent sadness and loss of interest.",
        "prevention": "Stress management, social support, early counseling.",
        "care": "Psychotherapy, antidepressant medications, lifestyle adjustments."
    },
    "anxiety": {
        "title": "Anxiety Disorders",
        "info": "Mental health conditions involving excessive fear or worry.",
        "prevention": "Stress management, relaxation techniques.",
        "care": "Therapy, anti-anxiety medications, lifestyle changes."
    },
    "schizophrenia": {
        "title": "Schizophrenia",
        "info": "A severe mental disorder affecting thoughts, emotions, and behaviors.",
        "prevention": "Early intervention and reducing risk factors like drug abuse.",
        "care": "Antipsychotic medications, therapy, community support."
    }
}
    # add your other diseases here ...

# === Helper: fuzzy disease matching ===
def match_disease(name: str):
    diseases = list(KNOWLEDGE_BASE.keys())
    best_match = difflib.get_close_matches(name.lower(), diseases, n=1, cutoff=0.6)
    return best_match[0] if best_match else None

# === Chat State (memory) ===
chat_state = {"current_disease": None}

def get_bot_response(user_message: str) -> str:
    user_message = user_message.lower().strip()
    words = user_message.split()

    # --- Handle greetings ---
    greetings = ["hello", "hi", "hey", "good morning", "good evening"]
    if any(greet in user_message for greet in greetings):
        return "Hello! 👋 I’m HealthBot. I can provide information on diseases, their symptoms, prevention, and care. Try asking me about dengue, malaria, or another disease."

    disease = None
    category = None

    # Detect disease
    for word in words:
        if match_disease(word):
            disease = match_disease(word)
            break

    # Detect category
    for w in ["symptoms", "info", "prevention", "care", "treatment"]:
        if w in words:
            category = w
            break

    # Case 1: disease + category given
    if disease and category:
        if "symptom" in category or "info" in category:
            return KNOWLEDGE_BASE[disease]["info"]
        elif "prevent" in category:
            return KNOWLEDGE_BASE[disease]["prevention"]
        elif "care" in category or "treatment" in category:
            return KNOWLEDGE_BASE[disease]["care"]

    # Case 2: only disease given
    if disease and not category:
        chat_state["current_disease"] = disease
        return f"You asked about {KNOWLEDGE_BASE[disease]['title']}. Do you want to know about 'symptoms', 'prevention', or 'care'?"

    # Case 3: already stored disease, now expecting category
    if chat_state["current_disease"] and not disease:
        d = chat_state["current_disease"]
        if "symptom" in user_message or "info" in user_message:
            chat_state["current_disease"] = None
            return KNOWLEDGE_BASE[d]["info"]
        elif "prevent" in user_message:
            chat_state["current_disease"] = None
            return KNOWLEDGE_BASE[d]["prevention"]
        elif "care" in user_message or "treatment" in user_message:
            chat_state["current_disease"] = None
            return KNOWLEDGE_BASE[d]["care"]
        else:
            return "Please type 'symptoms', 'prevention', or 'care'."

    # Fallback
    return "Sorry, I didn’t recognize that. Try again (e.g., 'dengue prevention')."

# === FastAPI Setup ===
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Serve index.html at root
@app.get("/")
def read_index():
    return FileResponse("index.html")

class ChatRequest(BaseModel):
    message: str

@app.post("/chat")
def chat(req: ChatRequest):
    reply = get_bot_response(req.message)
    return {"reply": reply}

