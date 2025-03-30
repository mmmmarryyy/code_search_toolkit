import os
import logging
from collections import defaultdict

def combine_results(results, combination, query_file, results_folder):
    try:
        method_results = {}
        if 'CCAligner' in results:
            method_results['CCAligner'] = read_ccaligner_results(results['CCAligner'], query_file)
            print(f"CCAligner results len = ${len(method_results['CCAligner'])}")
        if 'CCSTokener' in results:
            method_results['CCSTokener'] = read_ccstokener_results(results['CCSTokener'], query_file)
            print(f"CCSTokener results len = ${len(method_results['CCSTokener'])}")
        if 'NIL-fork' in results:
            method_results['NIL-fork'] = read_nil_fork_results(results['NIL-fork'], query_file)
            print(f"NIL-fork results len = ${len(method_results['NIL-fork'])}")

        strategy = combination.get('strategy', 'intersection_union')
        if strategy == 'intersection_union':
            final_pairs = intersection_strategy(method_results)
        elif strategy == 'weighted_union':
            weights = combination.get('weights', {'CCAligner': 1, 'CCSTokener': 1, 'NIL-fork': 1})
            threshold = combination.get('threshold', 0.5)
            final_pairs = weighted_union_strategy(method_results, weights, threshold)
        else:
            raise ValueError(f"Unknown strategy: {strategy}")

        output_dir = os.path.join(results_folder, 'final_results')
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, 'final_results.txt')

        print(f"before writing result to {output_path}")
        
        with open(output_path, 'w') as f:
            for pair in final_pairs:
                f.write(f"{pair[0][0]},{pair[0][1]},{pair[0][2]},{pair[1][0]},{pair[1][1]},{pair[1][2]}\n")

        print(f"after writing result to {output_path}")
        
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
                            # print(f"\nDEBUG CCAligner: left_path = {left_path}, right_path = {right_path}\n")
                            if left_path != query_file and right_path != query_file:
                                continue
                            if (left_path == query_file):
                                clones.append((
                                    (left_path, int(parts[1]), int(parts[2])),
                                    (right_path, int(parts[4]), int(parts[5]))))
                            else:
                                clones.append((
                                    (right_path, int(parts[4]), int(parts[5])),
                                    (left_path, int(parts[1]), int(parts[2]))))
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
                        # print(f"\nDEBUG CCSTOKENER: left_path = {left_path}, right_path = {right_path}\n")
                        if left_path != query_file and right_path != query_file:
                            continue
                        if (left_path == query_file):
                            clones.append((
                                (left_path, int(parts[1]), int(parts[2])),
                                (right_path, int(parts[4]), int(parts[5]))))
                        else:
                            clones.append((
                                (right_path, int(parts[4]), int(parts[5])),
                                (left_path, int(parts[1]), int(parts[2]))))
                    # else:
                    #     print(f"\nDEBUG CCSTOKENER: parts[0] = {parts[0]}, parts[3] = {parts[3]}\n")
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
                        # print(f"\nDEBUG NIL: left_path = {left_path}, right_path = {right_path}\n")
                        if left_path != query_file and right_path != query_file:
                            continue
                        if (left_path == query_file):
                            clones.append((
                                (left_path, int(parts[1]), int(parts[2])),
                                (right_path, int(parts[4]), int(parts[5]))))
                        else:
                            clones.append((
                                (right_path, int(parts[4]), int(parts[5])),
                                (left_path, int(parts[1]), int(parts[2]))))
    except Exception as e:
        logging.warning(f"Error reading NIL-fork results: {str(e)}")
    return clones

def intersection_strategy(results):
    common = set.intersection(*[set(clones) for clones in results.values()])
    print(f"inside intersection_common; len(common) = {len(common)}")
    return sorted(common)

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