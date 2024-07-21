# Mondrian Anonymization Project


This project implements the Mondrian anonymization algorithm to anonymize a dataset, ensuring that sensitive information is protected while retaining the utility of the data. The project supports both numerical and categorical columns, with the use of JSON files for handling categorical data. A random perturbation technique is implemented for sensititve data in order to avoid re-identification. Additionally, it includes a script to generate a synthetic dataset for testing the anonymization process. 

## Overview
The project consists of:

- **Data Generation** : 
A script generates a synthetic dataset containing personal information such as name, gender, city, age, profession, education, and annual income. The distributions of attributes are sourced from ISTAT, the official source of Italian statistics.

- **Anonymization** :
The Mondrian algorithm is implemented to anonymize the dataset by generalizing quasi-identifiers while preserving data utility and sensitive data.

- **Random Perturbation** :
In order to avoid re-identification, a script applies random perturbation on sensitive data, preserving mean and variance of each sensitive attribute so that utility is maintained.

## Instructions :

The requirments for using our project are:
- Faker
- Pandas
- Numpy
- Matplotlib

Clone the repository:

```sh
git clone https://github.com/Alebasso01/K-anonymity.git
```

Install the requirments:
```sh
pip install faker pandas numpy matplotlib
```

Run the mondrian:
```sh
python mondrian.py
```





  

## Parameters

- **database**: The input dataset.
- **k**: The k-anonymity parameter.
- **qis**: List of quasi-identifiers (both numerical and categorical).
- **sd**: List of sensitive attributes.
- **ei**: List of explicit identifiers to be dropped.
- **json_files**: Dictionary mapping categorical quasi-identifiers to JSON file paths for LCA.
- **statistic**: Method for numerical quasi-identifier generalization ('range' or 'mean').

## Test

In the project we analyzed both mean and variance. Numerical attributes undergo mean and variance calculation, while categorical attributes are mapped based on hierarchical ordering where feasible. Additionally, a discernibility penalty function was implemented to quantify the uniqueness of quasi-identifiers, enhancing the anonymization process and ensuring robust data protection. We also included a function to calculate the equivalence size metric, which provides an additional measure of the quality of the k-anonymization. 

