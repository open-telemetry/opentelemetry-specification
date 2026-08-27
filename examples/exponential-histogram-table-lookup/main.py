# Copyright The OpenTelemetry Authors
# SPDX-License-Identifier: Apache-2.0

import argparse
import math

FRACTION_BITS = 52


def generate_boundaries(scale: int) -> list[int]:
    n = 1 << scale
    boundaries = [0, 1]

    for k in range(1, n):
        value = 1 << (FRACTION_BITS * n + k)
        for _ in range(scale):
            value = ceil_sqrt(value)
        boundaries.append(value & ((1 << FRACTION_BITS) - 1))

    boundaries.extend((1 << FRACTION_BITS, 1 << FRACTION_BITS))
    return boundaries


def ceil_sqrt(value: int) -> int:
    root = math.isqrt(value)
    return root if root * root == value else root + 1


def generate_index_table(
    scale: int, boundaries: list[int]
) -> tuple[list[int], int]:
    n = 1 << scale
    shift = 51 - scale
    table = []
    j = 0
    for i in range(2 * n):
        lower_bound = i << shift
        while lower_bound >= boundaries[j + 1]:
            j += 1
        table.append(j)
    return table, shift


def print_tables(
    scale: int, shift: int, boundaries: list[int], index_table: list[int]
) -> None:
    print(f"SCALE = {scale}")
    print(f"SHIFT = {shift}")
    print("BOUNDARIES = [")
    for start in range(0, len(boundaries), 4):
        values = boundaries[start : start + 4]
        print("    " + "".join(f"0x{value:013X}," for value in values))
    print("]")
    print("INDEX_TABLE = [")
    for start in range(0, len(index_table), 16):
        values = index_table[start : start + 16]
        print("    " + "".join(f"{value}," for value in values))
    print("]")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--scale", type=int, default=8, choices=range(1, 17))
    args = parser.parse_args()

    boundaries = generate_boundaries(args.scale)
    index_table, shift = generate_index_table(args.scale, boundaries)
    print_tables(args.scale, shift, boundaries, index_table)


if __name__ == "__main__":
    main()
