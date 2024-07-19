import pandas as pd
import numpy as np
import json

def check_k_anonymity(df, quasi_identifiers, k):
    group_sizes = df.groupby(quasi_identifiers).size()
       
    is_k_anonymous = (group_sizes >= k).all()

    if is_k_anonymous:
        print(f"Dataset k-anonymized with k = {k} ")
    else:
        print(f"Dataset does not respet k-anonymity with k = {k}")
        print("\nThese partitions does not respect k-anonymity:")
        print(group_sizes[(group_sizes < k)])
    
    return is_k_anonymous


def calculate_mean(column):
    try:
        col_no_brackets = column.strip('[]')
        if '-' in col_no_brackets:
            # statistic was a range so we calculate the mean
            col_split = col_no_brackets.split('-')
            return np.mean([int(col_split[0]), int(col_split[1])])
        else:
            # statistic was mean so it is a float
            return float(col_no_brackets)
    except (IndexError, ValueError):
        return np.nan
    
    
def create_mapping(levels, start_value=1):  # starting from 1, so we exclude ANY in json files"
    mapping = {}
    def recursive_map(levels, current_value):
        for level in levels:
            if 'categories' in level and level['categories']:
                mapping[level['name']] = current_value
                for sub_level in level['categories']:
                    mapping[sub_level['name']] = current_value
                current_value += 1
            else:
                mapping[level['name']] = current_value
                current_value += 1
        return current_value

    recursive_map(levels['categories'], start_value)
    return mapping

with open('generation\\json\\educations.json', 'r') as f:
    education_levels = json.load(f)

education_mapping = create_mapping(education_levels)

gender_mapping = {
    "male": 0,
    "female": 1
}

def mapping(col):
    if col == 'education':
        return education_mapping
    elif col == 'gender':
        return gender_mapping
    
ordinal_qis = ['education', 'gender']

def statistical_analysis(original_df, anonymized_df, all_qis, numerical_qis, ordinal_qis):
    original_df = original_df[all_qis].copy()
    anonymized_df = anonymized_df[all_qis].copy()

    print("Analysis of numerical columns:")
    for col in numerical_qis:
        anonymized_df.loc[:, col] = anonymized_df[col].apply(calculate_mean)

        mean_original = original_df[col].mean()
        mean_anonymized = anonymized_df[col].mean()
        std_original = original_df[col].std()
        std_anonymized = anonymized_df[col].std()

        print(f"Column: {col}")
        print(f"  Original mean: {mean_original}")
        print(f"  Anonymized mean: {mean_anonymized}")
        print(f"  Original standard deviation: {std_original}")
        print(f"  Anonymized standard deviation: {std_anonymized}")
        
    print("Analysis of ordinal categorical columns:")
    for col in ordinal_qis:
        col_mapping = mapping(col)
        original_df.loc[:, col] = original_df[col].map(col_mapping)
        anonymized_df.loc[:, col] = anonymized_df[col].map(col_mapping)
        
        anonymized_filtered = anonymized_df[anonymized_df[col].notna()]
        original_filtered = original_df[original_df[col].notna()]
        
        mean_anonymized = anonymized_filtered[col].mean()
        var_anonymized = anonymized_filtered[col].var()
        mean_original = original_filtered[col].mean()
        var_original = original_filtered[col].var()
        
        print(f"Column: {col}")
        print(f"  Original mean: {mean_original}")
        print(f"  Anonymized mean: {mean_anonymized}")
        print(f"  Original variance: {var_original}")
        print(f"  Anonymized variance: {var_anonymized}")