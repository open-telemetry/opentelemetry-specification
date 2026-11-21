// Copyright The OpenTelemetry Authors
// SPDX-License-Identifier: Apache-2.0

package main

import (
	"math/big"
	"sort"
	"strconv"
	"testing"
)

func TestGenerateBoundaries(t *testing.T) {
	for _, scale := range []int{1, 4, 8} {
		t.Run(strconv.Itoa(scale), func(t *testing.T) {
			n := 1 << scale
			boundaries := generateBoundaries(scale)
			if len(boundaries) != n+2 {
				t.Fatal("unexpected boundary count")
			}
			if boundaries[0] != 0 || boundaries[1] != 1 ||
				boundaries[n+1] != 1<<fractionBits {
				t.Fatal("incorrect power-of-two adjustment or sentinels")
			}
			degree := big.NewInt(int64(n))
			for k := 1; k < n; k++ {
				if boundaries[k+1] <= boundaries[k] || boundaries[k+1] >= 1<<fractionBits {
					t.Fatalf("threshold %d is out of order or outside the fraction field", k)
				}
				full := new(big.Int).SetUint64(boundaries[k+1] + (1 << fractionBits))
				target := new(big.Int).Lsh(big.NewInt(1), uint(fractionBits*n+k))
				above := new(big.Int).Exp(full, degree, nil)
				previous := new(big.Int).Sub(full, big.NewInt(1))
				below := new(big.Int).Exp(previous, degree, nil)
				if below.Cmp(target) >= 0 || above.Cmp(target) <= 0 {
					t.Fatalf("threshold %d is not the first representable value above the boundary", k)
				}
			}
		})
	}
}

func TestGenerateIndexTable(t *testing.T) {
	for _, scale := range []int{1, 4, 8} {
		t.Run(strconv.Itoa(scale), func(t *testing.T) {
			boundaries := generateBoundaries(scale)
			table, shift := generateIndexTable(scale, boundaries)
			n := 1 << scale
			if len(boundaries) != n+2 || len(table) != 2*n || shift != 51-scale {
				t.Fatal("unexpected table dimensions or shift")
			}
			checkLookup := func(significand uint64) {
				t.Helper()
				bucket := int(table[significand>>shift])
				if significand >= boundaries[bucket+1] {
					bucket++
				}
				expected := sort.Search(len(boundaries), func(j int) bool {
					return boundaries[j] > significand
				}) - 1
				if bucket != expected {
					t.Fatalf("significand %d: bucket %d, want %d", significand, bucket, expected)
				}
			}
			for i, approx := range table {
				start := uint64(i) << shift
				end := start + (1 << shift) - 1
				if boundaries[approx] > start || start >= boundaries[approx+1] {
					t.Fatalf("entry %d violates the region-start invariant", i)
				}
				checkLookup(start)
				checkLookup(end)
			}
			for _, threshold := range boundaries[1 : n+1] {
				for _, significand := range []uint64{threshold - 1, threshold, threshold + 1} {
					checkLookup(significand)
				}
			}
		})
	}
}

func TestGenerateIndexTableScale16(t *testing.T) {
	const scale = 16
	const n = 1 << scale

	// Uniformly spaced boundaries exercise the entry width without the
	// cost of generating all exponential boundaries at scale 16.
	boundaries := make([]uint64, n+2)
	boundaries[1] = 1
	for k := 1; k < n; k++ {
		boundaries[k+1] = uint64(k) << (fractionBits - scale)
	}
	boundaries[n+1] = 1 << fractionBits

	table, shift := generateIndexTable(scale, boundaries)
	if len(table) != 2*n || shift != 51-scale {
		t.Fatal("unexpected table dimensions or shift")
	}
	for i, position := range table {
		start := uint64(i) << shift
		if boundaries[position] > start || start >= boundaries[position+1] {
			t.Fatalf("entry %d violates the region-start invariant at an aligned threshold", i)
		}
	}
	for i := len(table) - 2; i < len(table); i++ {
		if table[i] != n {
			t.Fatalf("entry %d: got %d, want %d", i, table[i], n)
		}
	}
	approx := table[len(table)-1]
	bucket := approx
	if (1<<fractionBits)-1 >= boundaries[approx+1] {
		bucket++
	}
	if index := bucket - 1; index != n-1 {
		t.Fatalf("largest significand at exponent zero: index %d, want %d", index, n-1)
	}
}
