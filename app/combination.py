import os
import logging
from collections import defaultdict, Counter
from app.models import MethodEnum

def combine_results(results, combination, query_file, results_folder):
    try:
        method_results = {}
        if MethodEnum.CCALIGNER.value in results:
            method_results[MethodEnum.CCALIGNER.value] = read_ccaligner_results(results[MethodEnum.CCALIGNER.value], query_file)
            print(f"DEBUG: CCAligner results len = {len(method_results[MethodEnum.CCALIGNER.value])}")
        if MethodEnum.CCSTOKENER.value in results:
            method_results[MethodEnum.CCSTOKENER.value] = read_ccstokener_results(results[MethodEnum.CCSTOKENER.value], query_file)
            print(f"DEBUG: CCSTokener results len = {len(method_results[MethodEnum.CCSTOKENER.value])}")
        if MethodEnum.NIL_FORK.value in results:
            method_results[MethodEnum.NIL_FORK.value] = read_nil_fork_results(results[MethodEnum.NIL_FORK.value], query_file)
            print(f"DEBUG: NIL-fork results len = {len(method_results[MethodEnum.NIL_FORK.value])}")
        if MethodEnum.CCALIGNER_FORK.value in results:
            method_results[MethodEnum.CCALIGNER_FORK.value] = read_ccaligner_fork_results(results[MethodEnum.CCALIGNER_FORK.value], query_file)
            print(f"DEBUG: CCALIGNER-fork results len = {len(method_results[MethodEnum.CCALIGNER_FORK.value])}")
        if MethodEnum.CCSTOKENER_FORK.value in results:
            method_results[MethodEnum.CCSTOKENER_FORK.value] = read_ccstokener_fork_results(results[MethodEnum.CCSTOKENER_FORK.value], query_file)
            print(f"DEBUG: CCSTOKENER-fork results len = {len(method_results[MethodEnum.CCSTOKENER_FORK.value])}")

        strategy = combination.get('strategy', 'intersection_union')
        if strategy == 'intersection_union':
            final_pairs =  threshold_union_strategy(method_results, len(method_results))
        elif strategy == 'weighted_union':
            weights = combination.get('weights', {})
            for method in weights:
                if method not in method_results:
                    raise ValueError(f"Weighted union: метод '{method}' отсутствует в результатах или не поддерживается")
            threshold = combination.get('threshold', 0.5)
            final_pairs = weighted_union_strategy(method_results, weights, threshold)
        elif strategy == 'union':
            final_pairs = union_strategy(method_results)
        elif strategy == 'threshold_union':
            min_methods = combination.get('min_methods', 1)
            final_pairs = threshold_union_strategy(method_results, min_methods)
        else:
            raise ValueError(f"Unknown strategy: {strategy}")

        output_dir = os.path.join(results_folder, 'final_results')
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, 'final_results.txt')

        with open(output_path, 'w') as f:
            for pair in final_pairs:
                f.write(f"{pair[0][0]},{pair[0][1]},{pair[0][2]},{pair[1][0]},{pair[1][1]},{pair[1][2]}\n")

        return output_path

    except Exception as e:
        logging.error(f"Aggregation failed: {str(e)}")
        raise

def read_ccaligner_results(result_dir, query_file):
    begin_of_path = "/app/dataset/"
    clones = []
    try:
        for filename in os.listdir(result_dir):
            if 'clones' in filename:
                with open(os.path.join(result_dir, filename), 'r') as f:
                    for line in f:
                        parts = line.strip().split(',')
                        if len(parts) == 6 and parts[0].startswith(begin_of_path) and parts[3].startswith(begin_of_path):
                            left_path = parts[0][len(begin_of_path):]
                            right_path = parts[3][len(begin_of_path):]
                            if left_path != query_file and right_path != query_file:
                                continue
                            if left_path == query_file:
                                clones.append((
                                    (left_path, int(parts[1]), int(parts[2])),
                                    (right_path, int(parts[4]), int(parts[5]))
                                ))
                            else:
                                clones.append((
                                    (right_path, int(parts[4]), int(parts[5])),
                                    (left_path, int(parts[1]), int(parts[2]))
                                ))
    except Exception as e:
        logging.warning(f"Error reading CCAligner results: {str(e)}")
    return clones

def read_ccstokener_results(result_dir, query_file):
    begin_of_path = "/data/input/"
    clones = []
    try:
        filepath = os.path.join(result_dir, 'clonepairs.txt')
        if os.path.exists(filepath):
            with open(filepath, 'r') as f:
                for line in f:
                    parts = line.strip().split(',')
                    if len(parts) == 6 and parts[0].startswith(begin_of_path) and parts[3].startswith(begin_of_path):
                        left_path = parts[0][len(begin_of_path):]
                        right_path = parts[3][len(begin_of_path):]
                        if left_path != query_file and right_path != query_file:
                            continue
                        if left_path == query_file:
                            clones.append((
                                (left_path, int(parts[1]), int(parts[2])),
                                (right_path, int(parts[4]), int(parts[5]))
                            ))
                        else:
                            clones.append((
                                (right_path, int(parts[4]), int(parts[5])),
                                (left_path, int(parts[1]), int(parts[2]))
                            ))
    except Exception as e:
        logging.warning(f"Error reading CCSTokener results: {str(e)}")
    return clones

def read_nil_fork_results(result_dir, query_file):
    begin_of_path = "/data/dataset/"
    clones = []
    try:
        filepath = os.path.join(result_dir, 'output.txt')
        if os.path.exists(filepath):
            with open(filepath, 'r') as f:
                for line in f:
                    parts = line.strip().split(',')
                    if len(parts) == 6 and parts[0].startswith(begin_of_path) and parts[3].startswith(begin_of_path):
                        left_path = parts[0][len(begin_of_path):]
                        right_path = parts[3][len(begin_of_path):]
                        if left_path != query_file and right_path != query_file:
                            continue
                        if left_path == query_file:
                            clones.append((
                                (left_path, int(parts[1]), int(parts[2])),
                                (right_path, int(parts[4]), int(parts[5]))
                            ))
                        else:
                            clones.append((
                                (right_path, int(parts[4]), int(parts[5])),
                                (left_path, int(parts[1]), int(parts[2]))
                            ))
    except Exception as e:
        logging.warning(f"Error reading NIL-fork results: {str(e)}")
    return clones


def read_ccaligner_fork_results(result_dir, query_file):
    begin_of_path = "/data/dataset/"
    clones = []
    try:
        filepath = os.path.join(result_dir, 'result.txt')
        if os.path.exists(filepath):
            with open(filepath, 'r') as f:
                for line in f:
                    parts = line.strip().split(',')
                    if len(parts) == 6 and parts[0].startswith(begin_of_path) and parts[3].startswith(begin_of_path):
                        left_path = parts[0][len(begin_of_path):]
                        right_path = parts[3][len(begin_of_path):]
                        if left_path != query_file and right_path != query_file:
                            continue
                        if left_path == query_file:
                            clones.append((
                                (left_path, int(parts[1]), int(parts[2])),
                                (right_path, int(parts[4]), int(parts[5]))
                            ))
                        else:
                            clones.append((
                                (right_path, int(parts[4]), int(parts[5])),
                                (left_path, int(parts[1]), int(parts[2]))
                            ))
    except Exception as e:
        logging.warning(f"Error reading CCAligner-fork results: {str(e)}")
    return clones


def read_ccstokener_fork_results(result_dir, query_file):
    begin_of_path = "/data/dataset/"
    clones = []
    try:
        # TODO: now output, some other file
        filepath = os.path.join(result_dir, 'result.txt')
        if os.path.exists(filepath):
            with open(filepath, 'r') as f:
                for line in f:
                    parts = line.strip().split(',')
                    if len(parts) == 6 and parts[0].startswith(begin_of_path) and parts[3].startswith(begin_of_path):
                        left_path = parts[0][len(begin_of_path):]
                        right_path = parts[3][len(begin_of_path):]
                        if left_path != query_file and right_path != query_file:
                            continue
                        if left_path == query_file:
                            clones.append((
                                (left_path, int(parts[1]), int(parts[2])),
                                (right_path, int(parts[4]), int(parts[5]))
                            ))
                        else:
                            clones.append((
                                (right_path, int(parts[4]), int(parts[5])),
                                (left_path, int(parts[1]), int(parts[2]))
                            ))
    except Exception as e:
        logging.warning(f"Error reading CCAligner-fork results: {str(e)}")
    return clones


def weighted_union_strategy(results, weights, threshold):
    scores = defaultdict(float)
    total_weight = sum(weights.values())

    for method, clones in results.items():
        weight = weights.get(method, 0)
        for pair in clones:
            scores[pair] += weight

    return [
        pair for pair, score in scores.items()
        if (score / total_weight) >= threshold
    ]

def union_strategy(results):
    all_pairs = set()
    for _, clones in results.items():
        all_pairs.update(clones)
    return all_pairs

def threshold_union_strategy(results, min_methods):
    counter = Counter()
    for method, clones in results.items():
        unique_in_this_method = set(clones)
        for pair in unique_in_this_method:
            counter[pair] += 1

    selected = [pair for pair, count in counter.items() if count >= min_methods]
    return selected
