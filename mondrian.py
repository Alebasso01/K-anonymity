import json
import pandas as pd

# Function to load JSON data from file
def load_json(filename):
    with open(filename, 'r') as file:
        data = json.load(file)
    return data


# Function to drop specified columns from a DataFrame
def drop_EI(df, EI):
    return df.drop(columns=EI)


def find_parents(node, target, path=None, key=None):
    """ Find the parents of a target"""
    if path is None:
        path = []

    current_name = node.get('name', None) if isinstance(node, dict) else None

    if isinstance(node, dict):
        # Caso in cui il nodo è un dizionario
        if key and node.get(key) == target:
            # Se è stato trovato il nodo target all'interno del dizionario
            return path + [current_name]

        for k, v in node.items():
            if isinstance(v, list) and target in v:
                # Se il nodo target è presente nella lista
                return path + [current_name]
            elif isinstance(v, (dict, list)):
                # Ricorsivamente cerca nei sotto-nodi
                result = find_parents(v, target, path + [current_name] if current_name else path, key)
                if result:
                    return result
    elif isinstance(node, list):
        # Caso in cui il nodo è una lista
        for item in node:
            if isinstance(item, (dict, list)):
                # Ricorsivamente cerca nei sotto-nodi
                result = find_parents(item, target, path, key)
                if result:
                    return result
            elif item == target:
                # Se il nodo target è stato trovato nella lista
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

    # Rimuove i valori None e deduplica le liste di genitori
    parents1 = [parent for parent in parents1 if parent]
    parents2 = [parent for parent in parents2 if parent]

    # Trova l'antenato comune più basso confrontando i percorsi
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
        # Find column with highest cardinality (unique values) to split on
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
        # Ordina la partizione in base al quasi-identificatore corrente
        partition = partition.sort_values(by=qi)
        
        # Controlla se tutti i valori sono uguali per il quasi-identificatore corrente
        if partition[qi].iloc[0] != partition[qi].iloc[-1]:
            if qi in numerical_qis:
                if statistic == 'range':
                    # Se il quasi-identificatore è numerico, generalizza con il range di valori
                    min_val = partition[qi].iloc[0]
                    max_val = partition[qi].iloc[-1]
                    s = f"[{min_val}-{max_val}]"
                elif statistic == 'mean':
                    # Se il quasi-identificatore è numerico e la statistica è 'mean', generalizza con la media
                    mean_val = partition[qi].mean()
                    s = f"[{mean_val}]"
                else:
                    raise ValueError("Statistic must be 'range' or 'mean'")
            else:
                # Se il quasi-identificatore è categorico, cerca l'antenato comune più basso (LCA)
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
            
            # Sostituisce i valori del quasi-identificatore con la generalizzazione trovata
            partition[qi] = [s] * partition[qi].size
    
    return partition

def mondrian(database, k, qis, sd, ei, json_files):
    global dataframe_partitions
    dataframe_partitions = []

    database = drop_EI(database, ei)
    iterative_partition(database, k, sd)
    
    generalized_partitions = []
    for partition in dataframe_partitions:
        generalized_partition = generalize_partition(partition, qis, json_files, statistic='range')
        generalized_partitions.append(generalized_partition)
    
    anonymized_data = pd.concat(generalized_partitions, ignore_index=True)
    anonymized_data.to_csv('anonymized.csv', index=False)
    print("Dati anonimizzati salvati in anonymized.csv")
    
    # Print debugging information
    print(f"Numero di partizioni: {len(dataframe_partitions)}")
    total_rows = sum(len(partition) for partition in dataframe_partitions)
    print(f"Numero totale di righe nelle partizioni: {total_rows}")
    print(f"Numero originale di righe: {len(database)}")
    print(f"Numero totale di righe anonimizzate: {len(anonymized_data)}")


json_files = {
    'city': 'generation\\json\\cities.json',
    'profession': 'generation\\json\\jobs.json',
    'education': 'generation\\json\\educations.json',
    'gender': 'generation\\json\\genders.json'
}

k = 3

data = pd.read_csv("generation\\database.csv")

numerical_qis = ['age']
categorical_qis = ['gender', 'city', 'education', 'profession']
all_qis = categorical_qis + numerical_qis
explicit_identifier = ['person_id', 'first_name', 'last_name']
sensitive_data = ['annual_income']
statistic = "range"

anonymized_data = mondrian(data, k, all_qis, sensitive_data, explicit_identifier ,json_files)