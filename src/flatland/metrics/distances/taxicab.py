# taxicab distance with leniency factor
import math

import numpy as np

from flatland.metrics.distances import LENIENCY


def dist1d(p1, p2):
    return abs(p1["x"] - p2["x"]) + abs(p1["y"] - p2["y"])


def slope(p1, p2):
    num = p1["y"] - p2["y"]
    den = max(1e-10, p1["x"] - p2["x"])
    return num / den


def compare_circles(node1, node2):
    wt = 0
    wt += 0.1 * max(
        0, (1 - abs(node1["center"]["x"] - node2["center"]["x"]) / LENIENCY)
    )
    wt += 0.1 * max(
        0, (1 - abs(node1["center"]["y"] - node2["center"]["y"]) / LENIENCY)
    )

    raddiff = abs(node1["radius"] - node2["radius"]) / max(
        node1["radius"], node2["radius"]
    )
    wt += 0.1 * max(0, (1 - raddiff / LENIENCY))

    thetadiff = abs(node1.get("theta", 360) - node2.get("theta", 360))
    wt += 0.1 * max(0, (1 - thetadiff / LENIENCY))

    if wt != 0:
        wt += 0.6
    wt = np.round(wt, 2)
    return wt


def compare_lines(node1, node2):
    wt = 0
    dist_a = dist1d(node1["start"], node2["start"]) + dist1d(node1["end"], node2["end"])
    dist_b = dist1d(node1["start"], node2["end"]) + dist1d(node1["end"], node2["start"])

    distdiff = min(dist_a, dist_b)
    slopediff = np.abs(
        slope(node1["start"], node1["end"]) - slope(node2["start"], node2["end"])
    )
    lendiff = np.abs(
        dist1d(node1["start"], node1["end"]) - dist1d(node2["start"], node2["end"])
    )

    wt += max(0, (1 - distdiff / LENIENCY)) * 0.1
    wt += max(0, (1 - slopediff / LENIENCY)) * 0.1
    wt += max(0, (1 - lendiff / LENIENCY)) * 0.1

    if wt != 0:
        wt += 0.7
    wt = np.round(wt, 2)
    return wt


def node_weighter(node1, node2):
    if node1["type"] == node2["type"]:
        if node1["type"] == "circle":
            return compare_circles(node1, node2)
        elif node1["type"] == "line":
            return compare_lines(node1, node2)
    else:
        return 0


def edge_indicator(node1a, node1b, node2a, node2b):
    dist_1 = dist1d(node1a["center"], node1b["center"])
    dist_2 = dist1d(node2a["center"], node2b["center"])
    return abs(dist_1 - dist_2) <= LENIENCY
