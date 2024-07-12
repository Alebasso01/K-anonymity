import csv
import json

def load_education_levels(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        education_data = json.load(f)
    levels = []
    for category in education_data['categories']:
        if category['name'] == "Graduate School":
            for subcategory in category['categories']:
                levels.append(subcategory['name'])
        else:
            levels.append(category['name'])
    return levels

def generate_education_distribution_csv(filename, education_levels):
    education_distribution = {
        "18-24": [80, 10, 0, 0],
        "25-34": [70, 25, 3, 2],
        "35-44": [60, 30, 5, 5],
        "45-54": [55, 25, 10, 10],
        "55-64": [50, 20, 15, 15],
        "65-74": [45, 15, 20, 20],
        "75-90": [40, 10, 25, 25]
    }

    with open(filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['Age Range'] + education_levels)
        for age_range, distribution in education_distribution.items():
            writer.writerow([age_range] + distribution)

if __name__ == "__main__":
    education_levels = load_education_levels('generation\\json\\educations.json')
    generate_education_distribution_csv('generation\\csv\\education_distribution_by_age.csv', education_levels)
    print(f"File 'education_distribution_by_age.csv' creato con successo.")
