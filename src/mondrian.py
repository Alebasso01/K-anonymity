import json
import pandas as pd
from test import check_k_anonymity
from test import print_statistical_analysis
from random_perturbation import add_perturbation
from random_perturbation import print_mean_variance

def load_json(filename):
    """ Load a JSON file."""
    with open(filename, 'r') as file:
        data = json.load(file)
    return data


def drop_column(df, col):
    """ Drop a column from a DataFrame."""
    return df.drop(columns=col)


def find_parents(node, target, path=None, key=None):
    """ Find the parents of a target"""
    if path is None:
        path = []

    current_name = node.get('name', None) if isinstance(node, dict) else None

    if isinstance(node, dict):
        if key and node.get(key) == target:
            return path + [current_name]

        for k, v in node.items():
            if isinstance(v, list) and target in v:
                return path + [current_name]
            elif isinstance(v, (dict, list)):
                result = find_parents(v, target, path + [current_name] if current_name else path, key)
                if result:
                    return result
    elif isinstance(node, list):
        for item in node:
            if isinstance(item, (dict, list)):
                result = find_parents(item, target, path, key)
                if result:
                    return result
            elif item == target:
                return path + [current_name]

    return None

def find_target_parents_in_json(file_path, target, key=None):
    """ Find the parents of a target node in a JSON file."""
    with open(file_path, 'r') as file:
        data = json.load(file)

    return find_parents(data, target, key=key)


def find_lowest_common_ancestor(file_path, target1, target2, key=None):
    """ Find the lowest common ancestor of two nodes in a JSON file."""
    parents1 = find_target_parents_in_json(file_path, target1, key)
    parents2 = find_target_parents_in_json(file_path, target2, key)

    if not parents1 or not parents2:
        return None

    parents1 = [parent for parent in parents1 if parent]
    parents2 = [parent for parent in parents2 if parent]

    lca = None
    for p1, p2 in zip(parents1, parents2):
        if p1 == p2:
            lca = p1
        else:
            break

    return lca

def splitter(dataframe, column, k):
    """Splits the dataframe along a certain column respecting k value"""
    if column in dataframe.select_dtypes(include='number').columns:
        median_value = dataframe[column].median()
        left_partition = dataframe[dataframe[column] <= median_value]
        right_partition = dataframe[dataframe[column] > median_value]
    elif column in dataframe.select_dtypes(include='object').columns:
        sorted_values = sorted(dataframe[column])
        middle_index = len(sorted_values) // 2
        middle_value = sorted_values[middle_index]
        left_partition = dataframe[dataframe[column] <= middle_value]
        right_partition = dataframe[dataframe[column] > middle_value]
    else:
        # Skip columns that are neither numeric nor categorical
        return None, None
    
    if len(left_partition) >= k and len(right_partition) >= k and len(left_partition) < k*2 and len(right_partition) < k*2:
        return left_partition, right_partition
    else:
        # Adjust partitions if lengths are less than k
        left_partition = dataframe.iloc[:k]
        right_partition = dataframe.iloc[k:]
        return left_partition, right_partition


def iterative_partition(dataset, k, sensitive_data):
    """Splits the dataset in partitions iteratively."""
    
    def axe_to_split(dataframe, sensitive_data):
        # Find column with highest cardinality to split on
        columns_to_exclude = [col for col in dataframe.columns if col in sensitive_data]
        max_cardinality_column = dataframe.drop(columns_to_exclude, axis=1).nunique().idxmax()
        return max_cardinality_column
    
    stack = [dataset]
    while stack:
        current_dataset = stack.pop()
        if len(current_dataset) < k * 2:
            dataframe_partitions.append(current_dataset)
        else:
            axe = axe_to_split(current_dataset, sensitive_data)
            left_partition, right_partition = splitter(current_dataset, axe, k)
            
            if left_partition is not None and right_partition is not None:
                stack.append(left_partition)
                stack.append(right_partition)
            else:
                dataframe_partitions.append(current_dataset)


def generalize_partition(partition, qis, json_files, statistic):
    """ numerical quasi-identifiers are generalized using the statistic provided.
        categorical quasi-identifiers are generalized using the LCA"""
    numerical_qis = [qi for qi in qis if partition[qi].dtype in ['int64', 'float64']]
    
    for qi in qis:
        partition = partition.sort_values(by=qi)
        
        if partition[qi].iloc[0] != partition[qi].iloc[-1]:
            if qi in numerical_qis:
                if statistic == 'range':
                    min_val = partition[qi].iloc[0]
                    max_val = partition[qi].iloc[-1]
                    s = f"[{min_val}-{max_val}]"
                elif statistic == 'mean':
                    mean_val = partition[qi].mean()
                    s = f"[{mean_val}]"
                else:
                    raise ValueError("Statistic must be 'range' or 'mean'")
            else:
                unique_values = sorted(set(partition[qi]))
                if len(unique_values) == 1:
                    lca = unique_values[0]
                else:
                    lca = unique_values[0]
                    for value in unique_values[1:]:
                        lca_candidate = find_lowest_common_ancestor(json_files[qi], lca, value, key='name')
                        if lca_candidate:
                            lca = lca_candidate
                        else:
                            lca = 'ANY'
                            break
                        
                s = f"[{lca}]"
            
            partition[qi] = [s] * partition[qi].size
    
    return partition

def mondrian(database, k, qis, sd, ei, json_files, ordinal_qis, check=None):
    global dataframe_partitions
    dataframe_partitions = []

    database = drop_column(database, ei)
    iterative_partition(database, k, sd)
    
    generalized_partitions = []
    for partition in dataframe_partitions:
        generalized_partition = generalize_partition(partition, qis, json_files, statistic='range')
        generalized_partitions.append(generalized_partition)
    
    anonymized_data = pd.concat(generalized_partitions, ignore_index=True)
    perturbated_data = add_perturbation(anonymized_data, sensitive_data)
    perturbated_data.to_csv('src/data/anonymized.csv', index=False)
    print("Anonymized data saved in anonymized.csv")
    print(f"Number of partitions: {len(dataframe_partitions)}")
    
    if check is not None:
        print("Check anonymization: ")
        check_k_anonymity(anonymized_data, qis, k)
        print("Check mean and standard deviation after anonymization: ")
        print_statistical_analysis(database, anonymized_data, all_qis, numerical_qis, ordinal_qis)
        print_mean_variance(database, perturbated_data, sensitive_data)
    
json_files = {
    'city': 'generation\\json\\cities.json',
    'profession': 'generation\\json\\jobs.json',
    'education': 'generation\\json\\educations.json',
    'gender': 'generation\\json\\genders.json'
} 



k = 3

data = pd.read_csv("src/data/database.csv")

numerical_qis = ['age']
categorical_qis = ['gender', 'city', 'education', 'profession']
ordinal_qis = ['education', 'gender']
all_qis = categorical_qis + numerical_qis
explicit_identifier = ['person_id', 'first_name', 'last_name']
sensitive_data = ['annual_income']
statistic = "range"
check = True # da aggiungere per stampare la media e la deviazione standard del dataset originale e anonimizzato

anonymized_data = mondrian(data, k, all_qis, sensitive_data, explicit_identifier, json_files, ordinal_qis, check)