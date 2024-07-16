import csv
import json
import os
import random
import uuid
from faker import Faker

fake = Faker('it_IT')

def load_cities_from_file(filename):
    with open(filename, 'r') as f:
        cities_data = json.load(f)
    
    cities_list = []
    for region in cities_data['regions']:
        for state in region['states']:
            cities_list.extend(state['cities'])
    
    return cities_list

def load_csv_to_dict(filename):
    with open(filename, mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        return [row for row in reader]
    
def load_profession_mapping_from_csv(filename):
    profession_mapping = {}
    with open(filename, mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            education_level = row['Education Level']
            profession = row['Profession']
            if education_level not in profession_mapping:
                profession_mapping[education_level] = []
            profession_mapping[education_level].append(profession)
    return profession_mapping

def get_education_distribution_by_age(age, education_distribution):
    for row in education_distribution:
        age_range = row['Age Range'].split('-')
        if int(age_range[0]) <= age <= int(age_range[1]):
            levels = ['High School', "Bachelor's Degree", "Master's Degree", "Doctoral Degree"]
            percentages = [int(row[level]) if row[level] else 0 for level in levels]
            return random.choices(levels, weights=percentages, k=1)[0]
    return "High School"

def get_profession_by_education(education_level, profession_mapping):
    professions = profession_mapping.get(education_level, [])
    if not professions:
        raise ValueError(f"No professions found for education level: {education_level}")
    return random.choice(professions)

def get_annual_income_by_profession(profession, income_mapping):
    for row in income_mapping:
        categories = row['Categories'].split(",")
        if profession in categories:
            min_income, max_income = row['Average annual income (€)'].replace('€', '').replace(' ', '').split('-')
            min_income = int(min_income.replace(',', ''))
            max_income = int(max_income.replace(',', ''))
            return random.randint(min_income, max_income)
    return random.randint(20000, 40000)

gender_percentages = [48, 52]  # Male: 48%, Female: 52%

age_groups = ['18-29', '30-39', '40-49', '50-59', '60-69', '70-79', '80+']
age_percentages = [12.24, 13.65, 14.35, 15.76, 16.94, 15.53, 11.53]

def select_age():
    age_group = random.choices(age_groups, weights=age_percentages, k=1)[0]
    if age_group == '18-29':
        return random.randint(18, 29)
    elif age_group == '30-39':
        return random.randint(30, 39)
    elif age_group == '40-49':
        return random.randint(40, 49)
    elif age_group == '50-59':
        return random.randint(50, 59)
    elif age_group == '60-69':
        return random.randint(60, 69)
    elif age_group == '70-79':
        return random.randint(70, 79)
    else:
        return random.randint(80, 90)

def generate_fake_data(num_records, cities, genders, education_distribution, profession_mapping, income_mapping):
    data = []
    for _ in range(num_records):
        person_id = uuid.uuid4().hex[:8]
        gender = random.choices(genders, weights=gender_percentages, k=1)[0]
        first_name = fake.first_name_male() if gender == 'male' else fake.first_name_female()
        last_name = fake.last_name()
        city = random.choice(cities)
        age = select_age()
        education = get_education_distribution_by_age(age, education_distribution)
        profession = get_profession_by_education(education, profession_mapping)
        annual_income = get_annual_income_by_profession(profession, income_mapping)
        
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
    # Carica i dati dai file JSON e CSV
    cities = load_cities_from_file('C:\\Users\\bianc\\OneDrive\\Desktop\\python\\dpp_kanonymity\\K-anonymity\\generation\\json\\cities.json')
    genders = ['male', 'female']
    education_distribution = load_csv_to_dict('C:\\Users\\bianc\\OneDrive\\Desktop\\python\\dpp_kanonymity\\K-anonymity\\generation\\csv\\education_distribution_by_age.csv')
    profession_mapping = load_profession_mapping_from_csv('C:\\Users\\bianc\\OneDrive\\Desktop\\python\\dpp_kanonymity\\K-anonymity\\generation\\csv\\profession_by_education.csv')
    income_mapping = load_csv_to_dict('C:\\Users\\bianc\\OneDrive\\Desktop\\python\\dpp_kanonymity\\K-anonymity\\generation\\csv\\average_annual_income.csv')

    # Genera dati falsi
    num_records = 1000
    data = generate_fake_data(num_records, cities, genders, education_distribution, profession_mapping, income_mapping)

    # Salva i dati in un file CSV
    save_to_csv(data, 'database.csv')

    print("Dataset generato con successo e salvato in 'database.csv'.")
