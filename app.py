import difflib
import spacy
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# === Load lightweight NLP ===
nlp = spacy.blank("en")
if "sentencizer" not in nlp.pipe_names:
    nlp.add_pipe("sentencizer")

# === Knowledge Base (your existing one) ===
KNOWLEDGE_BASE = {
    "common_cold": {
        "title": "Common Cold",
        "info": "The common cold is a mild viral infection of the upper respiratory tract, mainly caused by rhinoviruses, adenoviruses, and coronaviruses. It spreads through airborne droplets or by touching contaminated surfaces. While generally harmless, it can cause discomfort and may lead to complications in people with weakened immunity.",
        "prevention": "Wash hands often, avoid touching your face, disinfect frequently touched objects, use tissues or your elbow when sneezing/coughing, and avoid close contact with sick individuals.",
        "care": "No cure exists. Care includes rest, drinking plenty of fluids, and using over-the-counter pain relievers, decongestants, or saline sprays. Symptoms usually improve in 7–10 days."
    },
    "influenza": {
        "title": "Influenza (Flu)",
        "info": "Influenza is a contagious respiratory illness caused by influenza viruses. It spreads rapidly through droplets when an infected person coughs, sneezes, or talks. It can range from mild to severe and may cause complications like pneumonia, especially in young children, the elderly, or people with chronic diseases.",
        "prevention": "Get annual flu vaccinations, wash hands often, avoid close contact with infected individuals, and maintain a healthy immune system.",
        "care": "Antiviral medications (e.g., oseltamivir) may be prescribed if started early. Supportive care includes rest, hydration, and fever reducers. Hospitalization may be required for severe cases."
    },
    "covid19": {
        "title": "COVID-19",
        "info": "COVID-19 is caused by the SARS-CoV-2 virus. It primarily spreads through respiratory droplets and close contact. Symptoms range from mild (fever, cough, fatigue) to severe (shortness of breath, pneumonia, organ failure). Some patients experience long-term effects, known as 'long COVID.'",
        "prevention": "Vaccination, mask-wearing in crowded spaces, hand hygiene, ventilation, and avoiding close contact with infected individuals.",
        "care": "Mild cases require rest, fluids, and fever management. Severe cases may need oxygen therapy, antivirals, corticosteroids, or intensive care. Long-term rehabilitation may be necessary for post-COVID symptoms."
    },
    "tuberculosis": {
        "title": "Tuberculosis (TB)",
        "info": "Tuberculosis is a bacterial infection caused by Mycobacterium tuberculosis, primarily affecting the lungs but can also impact other organs. It spreads through airborne droplets from coughing or sneezing. If untreated, TB can be life-threatening.",
        "prevention": "BCG vaccination, early detection and treatment of active TB cases, proper ventilation in living spaces, and wearing masks in high-risk areas.",
        "care": "Treatment requires a long course (6–9 months) of multiple antibiotics (e.g., isoniazid, rifampin). Directly Observed Therapy (DOT) is recommended to ensure compliance. Supportive care includes nutrition and rest."
    },
    "malaria": {
        "title": "Malaria",
        "info": "Malaria is a life-threatening disease caused by Plasmodium parasites, transmitted through bites of infected female Anopheles mosquitoes. Symptoms include fever, chills, and sweating, which may recur in cycles. Severe malaria can cause anemia, organ failure, and death.",
        "prevention": "Use insecticide-treated mosquito nets, insect repellents, protective clothing, and antimalarial prophylaxis when traveling to endemic regions.",
        "care": "Antimalarial drugs such as artemisinin-based combination therapy (ACT) are standard. Severe cases may need intravenous medications and supportive care in hospitals."
    },
    "dengue": {
        "title": "Dengue Fever",
        "info": "Dengue is a viral infection transmitted by Aedes mosquitoes. Symptoms include high fever, severe headache, muscle/joint pain, skin rash, and bleeding tendencies. Severe dengue (dengue hemorrhagic fever) can be fatal.",
        "prevention": "Eliminate mosquito breeding sites, use repellents and protective clothing, and install mosquito nets/screens. Community awareness is crucial.",
        "care": "There is no specific antiviral treatment. Care focuses on hydration, rest, and fever management with acetaminophen (not aspirin/NSAIDs, as they increase bleeding risk). Hospitalization may be required for severe cases."
    },
    "typhoid": {
        "title": "Typhoid Fever",
        "info": "Typhoid is a bacterial infection caused by Salmonella Typhi, usually spread through contaminated food or water. Symptoms include prolonged fever, abdominal pain, weakness, headache, and sometimes rash.",
        "prevention": "Drink safe water, maintain proper sanitation, practice hand hygiene, and consider vaccination if traveling to high-risk areas.",
        "care": "Treatment involves antibiotics (e.g., ciprofloxacin, ceftriaxone). Supportive care includes hydration, a nutritious diet, and rest. Severe cases may require hospitalization."
    },
    "cholera": {
        "title": "Cholera",
        "info": "Cholera is a severe diarrheal disease caused by Vibrio cholerae, usually spread through contaminated water or food. It can lead to rapid dehydration and shock if untreated.",
        "prevention": "Ensure access to clean drinking water, proper sanitation, handwashing, and food safety practices. Oral cholera vaccines are available in high-risk areas.",
        "care": "Immediate rehydration with Oral Rehydration Solution (ORS) is critical. Severe cases may need intravenous fluids and antibiotics (e.g., doxycycline)."
    },
    "asthma": {
        "title": "Asthma",
        "info": "Asthma is a chronic inflammatory disease of the airways that causes recurrent episodes of wheezing, breathlessness, chest tightness, and coughing. Triggers include allergens, pollution, exercise, and respiratory infections.",
        "prevention": "Avoid triggers (dust, smoke, allergens), maintain a healthy lifestyle, and get vaccinated against respiratory infections.",
        "care": "Asthma is managed with inhaled corticosteroids (to reduce inflammation) and bronchodilators (to open airways). Emergency inhalers are used during attacks. Long-term monitoring and adherence to treatment plans are essential."
    },
    "diabetes_type1": {
        "title": "Diabetes Type 1",
        "info": "Type 1 diabetes is an autoimmune condition where the immune system destroys insulin-producing beta cells in the pancreas. It usually develops in childhood or adolescence. Without insulin, blood sugar levels rise dangerously, leading to complications.",
        "prevention": "Currently, there is no known prevention for type 1 diabetes. Research is ongoing into genetic and environmental risk factors.",
        "care": "Lifelong insulin therapy is required. Patients must monitor blood sugar regularly, follow a healthy diet, exercise, and manage stress. Education about recognizing and managing hypoglycemia is critical."
    },
    "diabetes_type2": {
        "title": "Diabetes Type 2",
        "info": "Type 2 diabetes is a chronic condition where the body becomes resistant to insulin or does not produce enough of it. It is strongly linked to obesity, poor diet, physical inactivity, genetics, and aging. If uncontrolled, it can cause complications like heart disease, kidney failure, blindness, and nerve damage.",
        "prevention": "Maintain a healthy body weight, eat a balanced diet low in sugar and refined carbs, exercise regularly (at least 150 minutes per week), avoid smoking, and attend regular health check-ups.",
        "care": "Management includes lifestyle changes, oral medications like metformin, and in some cases insulin. Regular monitoring of blood glucose, cholesterol, and blood pressure is important. Patients may need routine eye, kidney, and foot check-ups to prevent complications."
    },
    "hypertension": {
        "title": "Hypertension (High Blood Pressure)",
        "info": "Hypertension is a chronic condition where blood pressure in the arteries is consistently elevated. Often called the 'silent killer,' it may not show symptoms but significantly increases the risk of stroke, heart disease, and kidney failure.",
        "prevention": "Adopt a low-salt, balanced diet, exercise regularly, maintain a healthy weight, avoid excessive alcohol and smoking, and manage stress.",
        "care": "Treatment may involve lifestyle modifications and antihypertensive medications (e.g., ACE inhibitors, beta-blockers, diuretics). Regular monitoring and long-term adherence to treatment are essential."
    },
    "stroke": {
        "title": "Stroke",
        "info": "A stroke occurs when blood flow to part of the brain is interrupted (ischemic stroke) or when a blood vessel bursts (hemorrhagic stroke). It causes brain cells to die within minutes. Symptoms include sudden weakness, confusion, trouble speaking, or loss of vision.",
        "prevention": "Control risk factors like hypertension, diabetes, and high cholesterol. Avoid smoking, exercise regularly, maintain a healthy weight, and eat a balanced diet.",
        "care": "Immediate medical attention is critical. Treatment may involve clot-busting drugs for ischemic stroke or surgery for hemorrhagic stroke. Long-term care includes physiotherapy, speech therapy, and lifestyle changes to prevent recurrence."
    },
    "heart_attack": {
        "title": "Heart Attack (Myocardial Infarction)",
        "info": "A heart attack occurs when blood flow to part of the heart muscle is blocked, usually by a blood clot in the coronary arteries. Symptoms include chest pain, shortness of breath, nausea, and sweating. It can be fatal without urgent treatment.",
        "prevention": "Manage risk factors like high cholesterol, hypertension, and diabetes. Adopt a heart-healthy diet, exercise, avoid smoking, and maintain a healthy weight.",
        "care": "Emergency care may include aspirin, clot-dissolving drugs, angioplasty, or bypass surgery. Long-term management includes lifestyle changes, medications (statins, beta-blockers), and cardiac rehabilitation."
    },
    "hepatitis_b": {
        "title": "Hepatitis B",
        "info": "Hepatitis B is a viral infection that attacks the liver and can cause both acute and chronic disease. It spreads through contact with infected blood, sexual transmission, or from mother to child during childbirth. Chronic infection can lead to liver cirrhosis or cancer.",
        "prevention": "Vaccination is the best prevention. Avoid sharing needles, practice safe sex, and ensure safe blood transfusions.",
        "care": "Acute cases usually resolve on their own with supportive care. Chronic cases may require antiviral medications (e.g., tenofovir, entecavir) and regular monitoring of liver function."
    },
    "hepatitis_c": {
        "title": "Hepatitis C",
        "info": "Hepatitis C is a viral liver infection spread mainly through contact with contaminated blood (e.g., unsafe injections, transfusions). Unlike hepatitis B, there is no vaccine. Chronic infection can lead to cirrhosis, liver failure, or liver cancer.",
        "prevention": "Avoid sharing needles, ensure safe blood transfusions, and use sterile medical equipment. Practice safe sex in high-risk situations.",
        "care": "Treatment includes direct-acting antiviral medications, which can cure most cases. Supportive care involves regular monitoring and avoiding alcohol or drugs that damage the liver."
    },
    "hiv_aids": {
        "title": "HIV/AIDS",
        "info": "Human Immunodeficiency Virus (HIV) attacks the immune system, weakening the body’s defense against infections. If untreated, it progresses to Acquired Immunodeficiency Syndrome (AIDS). HIV spreads through blood, sexual contact, or from mother to child.",
        "prevention": "Practice safe sex, avoid sharing needles, ensure safe blood products, and take preventive medicines like PrEP if at high risk.",
        "care": "There is no cure, but antiretroviral therapy (ART) allows people with HIV to live long, healthy lives. Treatment also includes monitoring for opportunistic infections and regular medical care."
    },
    "pneumonia": {
        "title": "Pneumonia",
        "info": "Pneumonia is an infection that inflames the air sacs in the lungs, which may fill with fluid or pus. It can be caused by bacteria, viruses, or fungi. Symptoms include cough, fever, chest pain, and difficulty breathing.",
        "prevention": "Vaccinations (pneumococcal, flu), good hygiene, and avoiding smoking help prevent pneumonia.",
        "care": "Bacterial pneumonia requires antibiotics. Viral pneumonia is treated with supportive care (rest, fluids, fever reducers). Severe cases may need hospitalization and oxygen therapy."
    },
    "measles": {
        "title": "Measles",
        "info": "Measles is a highly contagious viral infection spread through coughing and sneezing. Symptoms include high fever, cough, runny nose, conjunctivitis, and a characteristic rash. Complications can include pneumonia, encephalitis, and death.",
        "prevention": "Vaccination (MMR vaccine) is the best prevention. Isolate infected individuals to reduce spread.",
        "care": "There is no specific antiviral treatment. Care includes rest, hydration, vitamin A supplements, and treating symptoms. Severe cases may need hospitalization."
    },
    "mumps": {
        "title": "Mumps",
        "info": "Mumps is a contagious viral infection that primarily affects the salivary glands, causing swelling in the cheeks and jaw. It spreads through respiratory droplets. Complications include meningitis, orchitis (testicular inflammation), and hearing loss.",
        "prevention": "Vaccination (MMR vaccine) is highly effective. Good hygiene and avoiding contact with infected individuals help reduce spread.",
        "care": "Treatment is supportive: rest, hydration, pain relievers, and applying warm or cold packs to swollen glands. Most cases resolve in a few weeks."
    },
    "rubella": {
        "title": "Rubella (German Measles)",
        "info": "Rubella is a contagious viral infection that causes mild fever, rash, and swollen lymph nodes. It is especially dangerous for pregnant women, as it can cause congenital rubella syndrome in babies.",
        "prevention": "Vaccination (MMR vaccine) is the best protection. Pregnant women should avoid contact with infected individuals.",
        "care": "No specific treatment. Supportive care includes rest, hydration, and fever management. Most cases recover quickly."
    },
    "tuberculosis": {
        "title": "Tuberculosis (TB)",
        "info": "TB is a bacterial infection caused by Mycobacterium tuberculosis, mainly affecting the lungs but can spread to other organs. Symptoms include cough lasting more than 2 weeks, weight loss, night sweats, and fever.",
        "prevention": "BCG vaccination, good ventilation, mask usage in high-risk areas, and early detection and treatment of active cases.",
        "care": "Treatment involves a long course (6–9 months) of antibiotics such as isoniazid, rifampicin, pyrazinamide, and ethambutol. Adherence to therapy is crucial to prevent drug resistance."
    },
    "cholera": {
        "title": "Cholera",
        "info": "Cholera is an acute diarrheal infection caused by Vibrio cholerae bacteria, usually from contaminated water or food. It can cause severe dehydration and death within hours if untreated.",
        "prevention": "Ensure safe drinking water, proper sanitation, hand hygiene, and vaccination in high-risk areas.",
        "care": "Immediate rehydration with oral rehydration solution (ORS) is critical. Severe cases may need intravenous fluids and antibiotics like doxycycline or azithromycin."
    },
    "diphtheria": {
        "title": "Diphtheria",
        "info": "Diphtheria is a serious bacterial infection affecting the mucous membranes of the throat and nose. It produces toxins that can damage the heart, nerves, and kidneys. Symptoms include sore throat, fever, and a thick gray membrane in the throat.",
        "prevention": "DTaP/Tdap vaccination is the best protection. Isolate infected individuals to prevent spread.",
        "care": "Treatment includes diphtheria antitoxin and antibiotics (erythromycin or penicillin). Supportive care may be needed for breathing difficulties."
    },
    "whooping_cough": {
        "title": "Whooping Cough (Pertussis)",
        "info": "Pertussis is a highly contagious bacterial infection that causes severe coughing fits followed by a 'whooping' sound. It can be dangerous for infants and young children.",
        "prevention": "DTaP/Tdap vaccination, especially for children and pregnant women, is essential. Avoid close contact with infected individuals.",
        "care": "Antibiotics such as azithromycin or clarithromycin are used. Supportive care includes rest, hydration, and in severe cases, hospitalization with oxygen therapy."
    },
    "influenza": {
        "title": "Influenza (Flu)",
        "info": "Influenza is a viral respiratory illness that spreads through droplets. Symptoms include fever, cough, sore throat, muscle aches, and fatigue. Complications can include pneumonia and worsening of chronic diseases.",
        "prevention": "Annual flu vaccination, good hand hygiene, mask use, and avoiding close contact with sick individuals.",
        "care": "Antiviral medications (oseltamivir, zanamivir) may shorten illness if started early. Supportive care includes rest, fluids, and fever-reducing medications."
    },
    "covid19": {
        "title": "COVID-19",
        "info": "COVID-19 is caused by the SARS-CoV-2 virus. It spreads mainly through respiratory droplets and can range from mild symptoms to severe pneumonia, multi-organ failure, and death.",
        "prevention": "Vaccination, mask-wearing, good ventilation, hand hygiene, and social distancing in high-risk areas.",
        "care": "Mild cases need rest, fluids, and fever management. Severe cases may require hospitalization, oxygen, antivirals, or steroids. Long-term monitoring may be necessary for post-COVID conditions."
    },
    "malaria": {
        "title": "Malaria",
        "info": "Malaria is a mosquito-borne disease caused by Plasmodium parasites. Symptoms include fever, chills, sweating, and anemia. Severe malaria can lead to coma or death.",
        "prevention": "Use insecticide-treated mosquito nets, indoor spraying, prophylactic drugs in high-risk areas, and eliminating stagnant water.",
        "care": "Treatment depends on the Plasmodium species and severity. Artemisinin-based combination therapies (ACTs) are the standard treatment. Severe cases require intravenous artesunate."
    },
    "dengue": {
        "title": "Dengue Fever",
        "info": "Dengue is a mosquito-borne viral infection causing high fever, severe headache, joint and muscle pain, rash, and in severe cases, dengue hemorrhagic fever or shock syndrome.",
        "prevention": "Prevent mosquito bites by using nets, repellents, and removing breeding sites. Community mosquito control is important.",
        "care": "No specific antiviral treatment. Supportive care includes hydration, fever control (avoid aspirin/NSAIDs), and monitoring for warning signs. Severe cases may require hospitalization."
    },
    "typhoid": {
        "title": "Typhoid Fever",
        "info": "Typhoid is a bacterial infection caused by Salmonella typhi, spread through contaminated food and water. Symptoms include prolonged fever, abdominal pain, weakness, and constipation or diarrhea.",
        "prevention": "Safe drinking water, proper sanitation, good hygiene, and vaccination in high-risk areas.",
        "care": "Antibiotics (azithromycin, ceftriaxone, or fluoroquinolones where effective) are the main treatment. Rehydration and proper nutrition support recovery."
    },
    "hepatitis_a": {
        "title": "Hepatitis A",
        "info": "Hepatitis A is a viral liver infection transmitted mainly through contaminated food and water. It usually causes short-term illness with fatigue, jaundice, fever, and abdominal pain, but does not lead to chronic disease.",
        "prevention": "Vaccination, safe food and water practices, and proper sanitation are effective preventive measures.",
        "care": "No specific treatment. Supportive care with rest, hydration, and good nutrition helps recovery. Most people recover fully within weeks to months."
    },
    "hepatitis_b": {
        "title": "Hepatitis B",
        "info": "Hepatitis B is a viral infection that can cause both acute and chronic liver disease. It spreads through blood, sexual contact, or from mother to child during birth. Chronic infection increases the risk of liver cirrhosis and liver cancer.",
        "prevention": "Vaccination is the best prevention. Safe sex practices, avoiding sharing needles, and screening blood products are important.",
        "care": "Acute cases may only need supportive care. Chronic cases may require antiviral medications such as tenofovir or entecavir, and regular monitoring for liver damage."
    },
    "hepatitis_c": {
        "title": "Hepatitis C",
        "info": "Hepatitis C is a bloodborne viral infection that can cause both acute and chronic liver disease, often progressing silently for years before symptoms appear. Chronic infection can lead to cirrhosis and liver cancer.",
        "prevention": "No vaccine is available. Prevention involves avoiding needle sharing, safe blood transfusion practices, and safe sex practices.",
        "care": "Direct-acting antiviral (DAA) medications can cure most cases. Regular monitoring of liver function is important in chronic cases."
    },
    "ebola": {
        "title": "Ebola Virus Disease",
        "info": "Ebola is a severe, often fatal viral hemorrhagic fever. It spreads through direct contact with blood or bodily fluids of infected individuals or animals. Symptoms include fever, vomiting, diarrhea, bleeding, and organ failure.",
        "prevention": "Avoid contact with infected individuals, animals, or contaminated materials. Strict infection control practices in healthcare settings are essential.",
        "care": "Supportive treatment with fluids, electrolytes, oxygen therapy, and treatment of complications improves survival. Experimental antivirals and monoclonal antibodies may be used in outbreaks."
    },
    "zika": {
        "title": "Zika Virus",
        "info": "Zika is a mosquito-borne viral infection that usually causes mild symptoms like fever, rash, joint pain, and conjunctivitis. However, infection during pregnancy can cause birth defects, including microcephaly.",
        "prevention": "Prevent mosquito bites by using repellents, nets, and eliminating standing water. Pregnant women should avoid traveling to Zika-affected areas.",
        "care": "No specific treatment. Supportive care with rest, hydration, and fever management is recommended. Most people recover fully."
    },
    "yellow_fever": {
        "title": "Yellow Fever",
        "info": "Yellow fever is a mosquito-borne viral infection causing fever, jaundice, bleeding, and organ failure in severe cases. It is common in parts of Africa and South America.",
        "prevention": "Vaccination is highly effective. Mosquito bite prevention and vector control are also important.",
        "care": "No specific antiviral treatment. Supportive care includes rest, hydration, and treatment of symptoms. Severe cases may require intensive care."
    },
    "leprosy": {
        "title": "Leprosy (Hansen’s Disease)",
        "info": "Leprosy is a chronic infectious disease caused by Mycobacterium leprae, affecting the skin, nerves, and mucous membranes. It leads to skin lesions, numbness, and deformities if untreated.",
        "prevention": "Early detection and treatment help prevent transmission. Avoid prolonged contact with untreated patients.",
        "care": "Multidrug therapy (MDT) with dapsone, rifampicin, and clofazimine is effective. Rehabilitation and reconstructive surgery may be needed in advanced cases."
    },
    "plague": {
        "title": "Plague",
        "info": "Plague is a severe bacterial infection caused by Yersinia pestis, spread through flea bites or contact with infected animals. Forms include bubonic (swollen lymph nodes), septicemic (blood infection), and pneumonic (lung infection).",
        "prevention": "Control rodent populations, use insect repellents, and avoid contact with infected animals. Protective measures are crucial during outbreaks.",
        "care": "Prompt antibiotic treatment with streptomycin, gentamicin, or doxycycline is lifesaving. Supportive care may be required in severe cases."
    },
    "meningitis": {
        "title": "Meningitis",
        "info": "Meningitis is inflammation of the protective membranes around the brain and spinal cord, caused by bacteria, viruses, or fungi. Symptoms include severe headache, stiff neck, fever, sensitivity to light, and confusion.",
        "prevention": "Vaccination (against meningococcal, pneumococcal, and Hib bacteria), good hygiene, and prompt treatment of infections help prevent meningitis.",
        "care": "Bacterial meningitis requires urgent intravenous antibiotics and corticosteroids. Viral meningitis is usually milder and treated with supportive care."
    },
    "polio": {
        "title": "Poliomyelitis (Polio)",
        "info": "Polio is a viral disease that can cause paralysis by attacking the nervous system. It mainly affects children under 5 and spreads through contaminated food, water, or contact with an infected person.",
        "prevention": "Polio vaccination (OPV or IPV) is the best protection. Maintaining hygiene and sanitation also prevents spread.",
        "care": "No cure exists. Supportive treatment includes physical therapy, mobility aids, and managing complications. Vaccination remains the key to eradication."
    },
    "tetanus": {
        "title": "Tetanus",
        "info": "Tetanus is a bacterial infection caused by *Clostridium tetani*, which produces a toxin affecting the nervous system. It leads to painful muscle stiffness and spasms, often starting with lockjaw, and can be life-threatening without treatment.",
        "prevention": "Routine tetanus vaccination (DTaP, Td, or Tdap) and proper wound care are highly effective preventive measures.",
        "care": "Immediate administration of tetanus antitoxin (immunoglobulin), antibiotics, muscle relaxants, and supportive hospital care."
    },
    "rabies": {
        "title": "Rabies",
        "info": "Rabies is a deadly viral infection transmitted through bites or saliva of infected animals. Once symptoms appear—such as hydrophobia, agitation, or paralysis—it is almost always fatal.",
        "prevention": "Vaccination for pets, avoiding stray animals, and post-exposure prophylaxis (PEP) after suspected exposure.",
        "care": "Urgent wound cleaning, rabies vaccination, and rabies immunoglobulin administration immediately after exposure. No cure exists once symptoms develop."
    },
    "hiv_aids": {
        "title": "HIV/AIDS",
        "info": "Human Immunodeficiency Virus (HIV) weakens the immune system, making the body vulnerable to infections. If untreated, it progresses to Acquired Immunodeficiency Syndrome (AIDS).",
        "prevention": "Safe sex practices, not sharing needles, HIV testing and screening of blood products, and preventive medications (PrEP).",
        "care": "Antiretroviral therapy (ART) is lifelong treatment that suppresses the virus, allowing patients to live long, healthy lives."
    },
    "measles": {
        "title": "Measles",
        "info": "Measles is a highly contagious viral disease that causes fever, cough, runny nose, red eyes, and a widespread skin rash. Complications may include pneumonia, encephalitis, or death in severe cases.",
        "prevention": "MMR (measles, mumps, rubella) vaccination provides effective prevention.",
        "care": "No specific antiviral treatment. Supportive care includes rest, hydration, fever management, and vitamin A supplementation."
    },
    "mumps": {
        "title": "Mumps",
        "info": "Mumps is a viral infection that causes swelling of the salivary glands, fever, headache, and muscle aches. In some cases, it can cause complications such as meningitis, orchitis, or hearing loss.",
        "prevention": "MMR vaccination is the best preventive measure.",
        "care": "No specific treatment. Supportive care with rest, hydration, and pain relievers helps recovery."
    },
    "rubella": {
        "title": "Rubella (German Measles)",
        "info": "Rubella is a mild viral illness causing rash, low fever, and joint pain. While generally mild, infection during pregnancy can cause congenital rubella syndrome (CRS), leading to serious birth defects.",
        "prevention": "MMR vaccination provides effective prevention.",
        "care": "Supportive care includes rest, hydration, and pain relief. No specific antiviral exists."
    },
    "chikungunya": {
        "title": "Chikungunya",
        "info": "Chikungunya is a mosquito-borne viral disease characterized by sudden fever and severe joint pain. Other symptoms may include headache, rash, and fatigue. Although rarely fatal, joint pain can persist for months.",
        "prevention": "Mosquito control, repellents, protective clothing, and community awareness reduce spread.",
        "care": "No specific treatment. Supportive care with fluids, rest, and pain relievers (paracetamol, not aspirin) is recommended."
    },
    "hantavirus": {
        "title": "Hantavirus Pulmonary Syndrome (HPS)",
        "info": "Hantavirus is a rare but severe respiratory disease transmitted through contact with infected rodent droppings, urine, or saliva. It causes fever, muscle aches, and rapidly progressing respiratory failure.",
        "prevention": "Avoid rodent exposure by sealing homes, cleaning safely, and using protective gear in barns or sheds.",
        "care": "No specific cure exists. Supportive hospital care with oxygen therapy and intensive monitoring improves survival."
    },
    "ringworm": {
        "title": "Ringworm (Dermatophytosis)",
        "info": "Ringworm is a contagious fungal infection of the skin, scalp, or nails. It appears as red, circular, itchy patches on the skin. It spreads through contact with infected people, animals, or contaminated surfaces.",
        "prevention": "Maintain good hygiene, keep skin dry, avoid sharing towels or clothing, and treat pets if infected.",
        "care": "Topical antifungal creams (clotrimazole, terbinafine) or oral antifungals for severe infections."
    },
    "athletes_foot": {
        "title": "Athlete’s Foot (Tinea Pedis)",
        "info": "Athlete’s foot is a fungal infection that usually begins between the toes, causing itching, burning, and peeling skin. It thrives in warm, moist environments like sweaty shoes.",
        "prevention": "Keep feet clean and dry, wear breathable footwear, and avoid walking barefoot in public showers or pools.",
        "care": "Topical antifungal creams or powders. Severe cases may need oral antifungal medication."
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

class ChatRequest(BaseModel):
    message: str

@app.post("/chat")
def chat(req: ChatRequest):
    reply = get_bot_response(req.message)
    return {"reply": reply}
@app.get("/")
def read_root():
    return {"Hello": "World"}





