import numpy as np
import pandas as pd


def compute_mean_variance(column):
    mean = np.mean(column)
    variance = np.var(column, ddof=1)  # ddof=1 per ottenere la varianza campionaria
    return mean, variance


def print_mean_variance(original_df, perturbated_df, sensitive_data):
    column_name = sensitive_data[0]
    column_original = original_df[column_name].values
    column_perturbated = perturbated_df[column_name].values
    mean_original, variance_original = compute_mean_variance(column_original)
    mean_perturbated, variance_perturbated = compute_mean_variance(column_perturbated)
    print(f"Column: {column_name}")
    print(f"  Original mean: {mean_original}")
    print(f"  Perturbated mean: {mean_perturbated}")
    print(f"  Original variance: {variance_original}")
    print(f"  Perturbated variance: {variance_perturbated}")


def generate_small_perturbation(variance, size, perturbation_scale=0.1):
    mean_perturbation = 0
    perturbation_variance = variance * perturbation_scale
    perturbation = np.random.normal(mean_perturbation, np.sqrt(perturbation_variance), size)
    return perturbation


def add_perturbation(data, sensitive_data, min_value=0, perturbation_scale=0.1):
    column_name = sensitive_data[0]
    column = data[column_name].values
    mean_original, variance_original = compute_mean_variance(column)
    perturbation = generate_small_perturbation(variance_original, column.shape[0], perturbation_scale)
    perturbed_column = column + perturbation
    
    mean_perturbed = np.mean(perturbed_column)
    perturbed_column_adjusted = perturbed_column - mean_perturbed + mean_original
    
    variance_perturbed = np.var(perturbed_column_adjusted, ddof=1)
    
    std_factor = np.sqrt(variance_original / variance_perturbed)
    perturbed_column_final = (perturbed_column_adjusted - mean_original) * std_factor + mean_original
    
    perturbed_column_final = np.round(perturbed_column_final).astype(int)  # arrotondamento a numero intero
    perturbed_column_final = np.maximum(perturbed_column_final, min_value)
    
    data[column_name] = perturbed_column_final
    
    return data