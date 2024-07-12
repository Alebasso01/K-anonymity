import csv
import json
import pandas as pd

# Funzione per caricare le categorie dal file JSON
def load_categories_from_json(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        jobs_data = json.load(f)
    
    categories = []

    def add_category_with_parent(category_name, parent_name):
        categories.append((parent_name, category_name))
    
    for category in jobs_data['categories']:
        category_name = category['name']
        for subcategory in category.get('categories', []):
            subcategory_name = subcategory['name']
            add_category_with_parent(subcategory_name, category_name)
            for specialty in subcategory.get('specialties', {}).values():
                if isinstance(specialty, dict) and 'items' in specialty:
                    for job in specialty['items']:
                        add_category_with_parent(job, subcategory_name)
    
    return categories

# Funzione per risalire il nodo padre e trovare lo stipendio
def find_income(category, income_data, parent_category):
    if category in income_data:
        return income_data[category]
    elif parent_category in income_data:
        return income_data[parent_category]
    else:
        return "N/A"

# Dati sugli stipendi
income_data = {
    "Doctor": "60,000 - 120,000",
    "Nurse": "30,000 - 45,000",
    "Therapist": "28,000 - 38,000",
    "Medical Technician": "25,000 - 35,000",
    "Civil Engineer": "35,000 - 50,000",
    "Software Developer": "30,000 - 55,000",
    "Electrical Engineer": "35,000 - 55,000",
    "Mechanical Engineer": "35,000 - 50,000",
    "Chemical Engineer": "35,000 - 55,000",
    "Management Engineer": "40,000 - 60,000",
    "Lawyer": "40,000 - 80,000",
    "Judge": "60,000 - 100,000",
    "Magistrate": "50,000 - 90,000",
    "Primary School Teacher": "25,000 - 35,000",
    "Lower Secondary-School Teacher": "28,000 - 40,000",
    "Higher Secondary-School Teacher": "30,000 - 45,000",
    "University Professor": "45,000 - 90,000",
    "Actor": "20,000 - 50,000",
    "Musician": "20,000 - 45,000",
    "Visual Artist": "20,000 - 40,000",
    "Dance": "20,000 - 35,000",
    "Chef": "25,000 - 45,000",
    "Waiter": "15,000 - 25,000",
    "Assembly Line Worker": "20,000 - 30,000",
    "Machine Operator": "22,000 - 32,000",
    "Quality Control Inspector": "25,000 - 35,000",
    "Electrician": "25,000 - 35,000",
    "Woodworker": "22,000 - 32,000",
    "Tailor": "20,000 - 30,000",
    "Leather Worker": "22,000 - 32,000",
    "Retail": "20,000 - 30,000",
    "Wholesale": "22,000 - 35,000",
    "Building": "25,000 - 40,000",
    "Civil Engineering": "35,000 - 50,000",
    "Hotel Management": "25,000 - 45,000",
    "Tourism Services": "22,000 - 35,000",
    "Farming": "20,000 - 30,000",
    "Agricultural Services": "25,000 - 40,000"
}

# Carica le categorie dal file JSON
categories = load_categories_from_json('generation\\json\\jobs.json')

# Prepara i dati per il dataframe
data = []
for parent_category, category in categories:
    income = find_income(category, income_data, parent_category)
    data.append([parent_category, category, income])

# Crea il dataframe
df = pd.DataFrame(data, columns=["Sectors", "Categories", "Average annual income (€)"])

# Stampa il dataframe
print(df)

# Salva il dataframe in un file CSV
df.to_csv("generation\\csv\\average_annual_income.csv", index=False)
print("File 'average_annual_income.csv' creato con successo.")
