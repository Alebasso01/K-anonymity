import csv
import json

def load_professions_from_file(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        jobs_data = json.load(f)
    
    jobs_list = {
        "High School": [],
        "Bachelor's Degree": [],
        "Master's Degree": [],
        "Doctoral Degree": []
    }

    def add_jobs_to_list(jobs, level):
        for job in jobs:
            if job not in jobs_list[level]:
                jobs_list[level].append(job)

    def process_specialties(specialties, level):
        if isinstance(specialties, dict):
            for specialty in specialties.values():
                if isinstance(specialty, dict):
                    items = specialty.get('items', [])
                    add_jobs_to_list(items, level)
                    if 'categories' in specialty:
                        process_specialties(specialty['categories'], level)
        elif isinstance(specialties, list):
            for specialty in specialties:
                if isinstance(specialty, dict):
                    items = specialty.get('items', [])
                    add_jobs_to_list(items, level)
                    if 'categories' in specialty:
                        process_specialties(specialty['categories'], level)

    def extract_jobs(categories, level):
        for category in categories:
            if 'categories' in category:
                for subcategory in category['categories']:
                    if 'specialties' in subcategory:
                        process_specialties(subcategory['specialties'], level)
                    if 'categories' in subcategory:
                        process_specialties(subcategory['categories'], level)

    for category in jobs_data['categories']:
        category_name = category['name']
        if category_name == "Factory" or category_name == "Food" or category_name == "Arts" or category_name == "Agriculture":
            extract_jobs([category], "High School")
        if category_name == "Engineering" or category_name == "Commerce" or category_name == "Tourism and Hospitality" :
            extract_jobs([category], "Bachelor's Degree")
        if category_name == "Health" or category_name == "Legal Profession" or category_name == "Professor" or category_name == "Engineering":
            extract_jobs([category], "Master's Degree")
            extract_jobs([category], "Doctoral Degree")
    
    return jobs_list

def generate_profession_by_education_csv(filename, professions_by_education):
    with open(filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['Education Level', 'Profession'])
        for education_level, professions in professions_by_education.items():
            for profession in professions:
                writer.writerow([education_level, profession])

if __name__ == "__main__":
    professions_by_education = load_professions_from_file('generation\\json\\jobs.json')
    generate_profession_by_education_csv('generation\\csv\\profession_by_education.csv', professions_by_education)
    print("File 'profession_by_education.csv' creato con successo.")
