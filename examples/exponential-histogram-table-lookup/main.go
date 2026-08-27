// Copyright The OpenTelemetry Authors
// SPDX-License-Identifier: Apache-2.0

package main

import (
	"flag"
	"fmt"
	"math/big"
)

const fractionBits = 52

func main() {
	scale := flag.Int("scale", 8, "table scale (1 through 16)")
	flag.Parse()
	if *scale < 1 || *scale > 16 {
		panic("scale must be between 1 and 16")
	}

	boundaries := generateBoundaries(*scale)
	indexTable, shift := generateIndexTable(*scale, boundaries)
	printTables(*scale, shift, boundaries, indexTable)
}

func generateBoundaries(scale int) []uint64 {
	n := 1 << scale
	boundaries := make([]uint64, 0, n+3)
	boundaries = append(boundaries, 0, 1)

	for k := 1; k < n; k++ {
		x := new(big.Int).Lsh(big.NewInt(1), uint(fractionBits*n+k))
		for i := 0; i < scale; i++ {
			x = ceilSqrt(x)
		}
		boundaries = append(
			boundaries,
			x.Uint64()&((1<<fractionBits)-1),
		)
	}

	return append(boundaries, 1<<fractionBits, 1<<fractionBits)
}

func ceilSqrt(value *big.Int) *big.Int {
	root := new(big.Int).Sqrt(value)
	squared := new(big.Int).Mul(new(big.Int).Set(root), root)
	if squared.Cmp(value) != 0 {
		root.Add(root, big.NewInt(1))
	}
	return root
}

func generateIndexTable(scale int, boundaries []uint64) ([]uint16, int) {
	n := 1 << scale
	shift := 51 - scale
	table := make([]uint16, 2*n)
	j := 0
	for i := range table {
		lowerBound := uint64(i) << shift
		for lowerBound >= boundaries[j+1] {
			j++
		}
		table[i] = uint16(j)
	}
	return table, shift
}

func printTables(
	scale int,
	shift int,
	boundaries []uint64,
	indexTable []uint16,
) {
	fmt.Printf("SCALE = %d\nSHIFT = %d\nBOUNDARIES = [\n", scale, shift)
	for i, value := range boundaries {
		if i%4 == 0 {
			fmt.Print("    ")
		}
		fmt.Printf("0x%013X,", value)
		if i%4 == 3 || i == len(boundaries)-1 {
			fmt.Println()
		}
	}
	fmt.Println("]\nINDEX_TABLE = [")
	for i, value := range indexTable {
		if i%16 == 0 {
			fmt.Print("    ")
		}
		fmt.Printf("%d,", value)
		if i%16 == 15 || i == len(indexTable)-1 {
			fmt.Println()
		}
	}
	fmt.Println("]")
}
