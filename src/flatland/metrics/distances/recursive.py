# recursive comparison of properties
import numpy as np


def numdiff(a, b, normalize=128):
    return 1 - abs(a - b) / normalize


def compare_subparts(part1, part2):
    if isinstance(part1, (int, float)):
        answer = numdiff(part1, part2)
    elif isinstance(part1, str):
        answer = float(part1 == part2)
    elif isinstance(part1, list):
        den = len(part1)
        if den != len(part2):
            return 0.0
        num = sum(compare_subparts(part1[i], part2[i]) for i in range(den))
        answer = num / den
    elif isinstance(part1, dict):
        common_keys = set(part1.keys()) & set(part2.keys())
        num = sum(compare_subparts(part1[k], part2[k]) for k in common_keys)
        answer = (num / len(part1)) * (num / len(part2))
    else:
        answer = 0
    return np.round(answer, 2)


def compare_circles(node1, node2):
    num = 0
    den = 0
    for k in node1.keys():
        if k in ("id", "theta"):
            continue
        a = compare_subparts(node1[k], node2[k])
        num += a
        den += 1
    num += numdiff(node1["theta"] % 360, node2["theta"] % 360, 360)
    den += 1
    wt = num / den
    return wt


def compare_lines(node1, node2):
    num = 0
    den = 0
    for k in node1.keys():
        if k in ("id", "start", "end", "center"):
            continue
        a = compare_subparts(node1[k], node2[k])
        num += a
        den += 1
    num += max(
        [
            compare_subparts(node1["start"], node2["start"])
            + compare_subparts(node1["end"], node2["end"]),
            compare_subparts(node1["start"], node2["end"])
            + compare_subparts(node1["end"], node2["start"]),
        ]
    )
    den += 2
    wt = num / den
    return wt


def node_weighter(node1, node2):
    if node1["type"] == node2["type"]:
        if node1["type"] == "circle":
            return compare_circles(node1, node2)
        elif node1["type"] == "line":
            return compare_lines(node1, node2)
        else:
            return 0
    else:
        return 0


def edge_indicator(node1a, node1b, node2a, node2b):
    dist_1 = compare_subparts(node1a["center"], node1b["center"])
    dist_2 = compare_subparts(node2a["center"], node2b["center"])
    return abs(dist_1 - dist_2) <= 5e-2
