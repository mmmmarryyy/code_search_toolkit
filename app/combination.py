import os
import glob
import logging
import xml.etree.ElementTree as ET
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
        if MethodEnum.NICAD.value in results:
            method_results[MethodEnum.NICAD.value] = read_nicad_results(results[MethodEnum.NICAD.value], query_file)
            print(f"DEBUG: NICAD results len = {len(method_results[MethodEnum.NICAD.value])}")
        if MethodEnum.SOURCERERCC.value in results:
            method_results[MethodEnum.SOURCERERCC.value] = read_sourcerercc_results(results[MethodEnum.SOURCERERCC.value], query_file)
            print(f"DEBUG: SOURCERERCC results len = {len(method_results[MethodEnum.SOURCERERCC.value])}")
        
        strategy = combination.get('strategy', 'union')
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
                            if left_path == query_file and right_path == query_file:
                                if int(parts[1]) < int(parts[4]):
                                    clones.append((
                                        (left_path, int(parts[1]), int(parts[2])),
                                        (right_path, int(parts[4]), int(parts[5]))
                                    ))
                                else:
                                    clones.append((
                                        (right_path, int(parts[4]), int(parts[5])),
                                        (left_path, int(parts[1]), int(parts[2]))
                                    ))
                            elif left_path == query_file:
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
                        if left_path == query_file and right_path == query_file:
                            if int(parts[1]) < int(parts[4]):
                                clones.append((
                                    (left_path, int(parts[1]), int(parts[2])),
                                    (right_path, int(parts[4]), int(parts[5]))
                                ))
                            else:
                                clones.append((
                                    (right_path, int(parts[4]), int(parts[5])),
                                    (left_path, int(parts[1]), int(parts[2]))
                                ))
                        elif left_path == query_file:
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
                        if left_path == query_file and right_path == query_file:
                            if int(parts[1]) < int(parts[4]):
                                clones.append((
                                    (left_path, int(parts[1]), int(parts[2])),
                                    (right_path, int(parts[4]), int(parts[5]))
                                ))
                            else:
                                clones.append((
                                    (right_path, int(parts[4]), int(parts[5])),
                                    (left_path, int(parts[1]), int(parts[2]))
                                ))
                        elif left_path == query_file:
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
                        if left_path == query_file and right_path == query_file:
                            if int(parts[1]) < int(parts[4]):
                                clones.append((
                                    (left_path, int(parts[1]), int(parts[2])),
                                    (right_path, int(parts[4]), int(parts[5]))
                                ))
                            else:
                                clones.append((
                                    (right_path, int(parts[4]), int(parts[5])),
                                    (left_path, int(parts[1]), int(parts[2]))
                                ))
                        elif left_path == query_file:
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
                        if left_path == query_file and right_path == query_file:
                            if int(parts[1]) < int(parts[4]):
                                clones.append((
                                    (left_path, int(parts[1]), int(parts[2])),
                                    (right_path, int(parts[4]), int(parts[5]))
                                ))
                            else:
                                clones.append((
                                    (right_path, int(parts[4]), int(parts[5])),
                                    (left_path, int(parts[1]), int(parts[2]))
                                ))
                        elif left_path == query_file:
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
        logging.warning(f"Error reading CCStokener-fork results: {str(e)}")
    return clones


def read_nicad_results(result_dir, query_file):
    begin_of_path = "nicadclones/dataset/dataset/"
    clones = []

    try:
        pattern = os.path.join(result_dir, "dataset_functions-blind-abstract-clones-*.xml")
        xml_files = glob.glob(pattern)
        if not xml_files:
            logging.warning(f"No NiCad XML files found in {result_dir}")
            return clones
        
        for xml_path in xml_files:
            try:
                tree = ET.parse(xml_path)
                root = tree.getroot()
            except ET.ParseError as e:
                logging.warning(f"Failed to parse {xml_path}: {e}")
                continue

            for clone_el in root.findall("clone"):
                sources = clone_el.findall("source")
                if len(sources) != 2:
                    continue

                parsed = []
                for src in sources:
                    file_attr = src.get("file", "")

                    if file_attr.startswith(begin_of_path):
                        file_rel = file_attr[len(begin_of_path):]
                    else:
                        file_rel = file_attr

                    try:
                        start = int(src.get("startline"))
                        end   = int(src.get("endline"))
                    except ValueError:
                        start = end = None

                    parsed.append((file_rel, start, end))

                paths = [p[0] for p in parsed]
                if query_file not in paths:
                    continue

                if parsed[0][0] == query_file and parsed[1][0] == query_file:
                    if parsed[0][1] < parsed[1][1]:
                        clones.append((parsed[0], parsed[1]))
                    else:
                        clones.append((parsed[1], parsed[0]))
                elif parsed[0][0] == query_file:
                    clones.append((parsed[0], parsed[1]))
                else:
                    clones.append((parsed[1], parsed[0]))
    
    except Exception as e:
        logging.warning(f"Error reading NiCad results: {str(e)}")
    return clones


def read_sourcerercc_results(result_dir, query_file):
    stats_pattern = os.path.join(result_dir, "*.stats")
    stats_files = glob.glob(stats_pattern)
    if not stats_files:
        logging.warning(f"No .stats files in {result_dir}")
        return []

    file_map = {}
    block_map = {}

    for stats_path in stats_files:
        with open(stats_path, "r") as sf:
            for line in sf:
                parts = [p.strip().strip('"') for p in line.split(",")]
                if not parts or len(parts) < 2:
                    continue
                code_type = parts[0] 
                code_id   = parts[1]
                if code_type.startswith("f"):
                    file_path = parts[2]
                    prefix = "projects/dataset.zip/data/dataset/"
                    if file_path.startswith(prefix):
                        rel = file_path[len(prefix):]
                    else:
                        rel = file_path
                    file_map[code_id] = rel

                elif code_type.startswith("b"):
                    if len(parts) < 8:
                        continue
                    try:
                        start = int(parts[6])
                        end   = int(parts[7])
                    except ValueError:
                        continue
                    block_map[code_id] = (start, end)

    pairs_path = os.path.join(result_dir, "results.pairs")
    if not os.path.exists(pairs_path):
        logging.warning(f"No results.pairs in {result_dir}")
        return []

    clones = []

    with open(pairs_path, "r") as pf:
        for line in pf:
            parts = line.strip().split(",")
            if len(parts) != 4:
                continue
            _, b1, _, b2 = parts

            if b1 not in block_map or b2 not in block_map:
                continue
            
            def find_file_id(block_id):
                for fid in file_map:
                    if block_id.endswith(fid):
                        return fid
                return None

            fid1 = find_file_id(b1)
            fid2 = find_file_id(b2)
            if not fid1 or not fid2:
                continue
            file1 = file_map[fid1]
            file2 = file_map[fid2]
            start1, end1 = block_map[b1]
            start2, end2 = block_map[b2]

            if file1 != query_file and file2 != query_file:
                continue


            if file1 == query_file and file2 == query_file:
                if start1 < start2:
                    clones.append(((file1, start1, end1), (file2, start2, end2)))
                else:
                    clones.append(((file2, start2, end2), (file1, start1, end1)))
            elif file1 == query_file:
                clones.append(((file1, start1, end1), (file2, start2, end2)))
            else:
                clones.append(((file2, start2, end2), (file1, start1, end1)))

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
