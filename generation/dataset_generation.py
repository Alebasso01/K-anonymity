import csv
import json
import os
import random
import uuid
from faker import Faker

fake = Faker('en_US')  # Specifica la lingua inglese per Faker

def load_cities_from_file(filename):
    with open(filename, 'r') as f:
        cities_data = json.load(f)
    
    cities_list = []
    for region in cities_data['regions']:
        for state in region['states']:
            cities_list.extend(state['cities'])
    
    return cities_list

def load_jobs_from_file(filename):
    with open(filename, 'r') as f:
        jobs_data = json.load(f)
    
    jobs_list = []
    for category in jobs_data['categories']:
        for subcategory in category.get('categories', []):  # Tratta il caso in cui 'categories' possa non essere presente o sia una lista vuota
            for specialty in subcategory.get('specialties', {}).values():  # Tratta il caso in cui 'specialties' possa non essere presente o sia un dizionario vuoto
                if isinstance(specialty, dict) and 'items' in specialty:
                    jobs_list.extend(specialty['items'])
    
    return jobs_list

def load_education_from_file(filename):
    with open(filename, 'r') as f:
        education_data = json.load(f)
    
    education_list = []
    for category in education_data['categories']:
        # Escludi la categoria "Graduate School" e includi i suoi sotto-categorie
        if category['name'] != 'Graduate School':
            education_list.append(category['name'])
        for subcategory in category['categories']:
            education_list.append(subcategory['name'])
    
    return education_list

def load_gender_from_file(filename):
    with open(filename, 'r') as f:
        gender_data = json.load(f)
    
    gender_list = [category['name'] for category in gender_data['categories']]
    
    return gender_list

def generate_fake_data(num_records, cities, jobs, educations, genders):
    data = []
    for _ in range(num_records):
        person_id = uuid.uuid4().hex[:8]
        gender = random.choice(genders)  # Selezione casuale tra 'male' e 'female'
        
        if gender == 'male':
            first_name = fake.first_name_male()
            last_name = fake.last_name_male()
        else:
            first_name = fake.first_name_female()
            last_name = fake.last_name_female()
        
        city = random.choice(cities)
        age = random.randint(18, 90)
        profession = random.choice(jobs)
        education = random.choice(educations)
        annual_income = random.randint(5000, 200000) // 1000 * 1000
        
        data.append([person_id, first_name, last_name, gender, city, age, profession, education, annual_income])
    
    return data

def save_to_csv(data, filename):
    current_dir = os.path.dirname(__file__) if __file__ else '.'
    file_path = os.path.join(current_dir, filename)
    
    with open(file_path, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['person_id', 'first_name', 'last_name', 'gender', 'city', 'age', 'profession', 'education', 'annual_income'])
        writer.writerows(data)

if __name__ == "__main__":
    # Carica i dati dai file JSON
    cities = load_cities_from_file('generation/cities.json')
    jobs = load_jobs_from_file('generation/jobs.json')
    educations = load_education_from_file('generation/educations.json')
    genders = load_gender_from_file('generation/genders.json')

    # Genera dati falsi
    num_records = 1000
    data = generate_fake_data(num_records, cities, jobs, educations, genders)

    # Salva i dati in un file CSV
    save_to_csv(data, 'database.csv')

    print(f"Dataset generato con successo e salvato in 'database.csv'.")
