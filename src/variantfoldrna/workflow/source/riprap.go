// Go implementation of the RipRap algorithm
// Original python code was obtained from

package main

import (
	"flag"
	"fmt"
	"io/ioutil"
	"math"
	"os"
	"os/exec"
	"strconv"
	"strings"
	"math/rand"
	"bufio"
	"sort"
	"github.com/dgryski/go-onlinestats"
	"time"

)
func main() {
	// Read in the command line inputs 
	seq := flag.String("seq", "", "Sequence")
	mutation := flag.String("mut", "", "Mutation")
	temp := flag.String("T", "", "Temperature")
	minWin := flag.String("minW", "", "Minimum window")
	flag.Parse()

	minWindow, err := strconv.Atoi(*minWin)
    if err != nil {
        // ... handle error
        panic(err)
    }

	// Check to make sure that we have a value for each of the inputs
	if *seq == "" || *mutation == "" || *temp == "" {
		flag.PrintDefaults()
		os.Exit(1)
	}

	// Check to make sure there are no N's in the sequence 
	if strings.Contains(*seq, "N") {
		fmt.Println("N is in the sequence")
		os.Exit(1)
	}

	// Get the reference allele 
	ref := string((*mutation)[0])
	println((*mutation)[1:len(*mutation)-1])
	// Get the position of the mutation
	pos, err := strconv.Atoi((*mutation)[1:len(*mutation)-1])
	
	// Check to see if there was an error when converting the mutation
	// position to an integer
	if err != nil {
		fmt.Println("Error converting position to integer:", err)
		os.Exit(1)
	}

	if string((*seq)[pos-1]) != ref {
		fmt.Println("Reference allele does not match sequence at position", pos)
		os.Exit(1)
	}

	if strings.Contains(*mutation, "N") {
		fmt.Println("N is in the mutation")
		os.Exit(1)
	}
	
	// Get the BPPMs for the Ref and Alt alleles 
	bppMatrix, nil := getBPPMatrix(*seq, *temp)
	bppMatrixMut, nil := getBPPMatrix(getMutatedSequence(*seq, *mutation), *temp)

	colSums := getSumMatrixCols(bppMatrix)
	colSumsMut := getSumMatrixCols(bppMatrixMut)

	
	if err != nil {
			fmt.Println("Error converting position to integer:")
			os.Exit(1)
		}

	score, _, _, _ := findRegion(colSums, colSumsMut, pos, minWindow)

	// Check that the values are valid
	if err != nil {
		fmt.Println("Error calculating Pearson correlation coefficient:", err)
		os.Exit(1)
	}

	fmt.Println(fmt.Sprintf("%f", score))

}



func getBPPMatrix(sequence string, temp string) ([][]float64, error) {
	// Create a temporary FASTA file with the given sequence
	tempFasta, name, err := createTempFasta(sequence)
	if err != nil {
		return nil, err
	}
	defer os.Remove(tempFasta) // Remove the temporary FASTA file when done

	// Execute RNAfold command
	output, err := exec.Command("RNAfold", "-p", "--noPS", "-i", tempFasta, "-T", temp).Output()
	if err != nil {
		return nil, fmt.Errorf("error running RNAfold: %w", err)
	}

	if output == nil {
		return nil, fmt.Errorf("error running RNAfold: %w", err)
	}

	// Parse output to extract base pair probability matrix
	bppMatrix  := parseOutput(".sq" + name + "_dp.ps", sequence)

	return bppMatrix, nil
}


func parseOutput(file_name string, sequence string) ([][]float64){

	bppMatrix := make([][]float64, len(sequence))
	for i := range bppMatrix {
		bppMatrix[i] = make([]float64, len(sequence))
	}

	file, _ := os.Open(file_name)

	defer file.Close()

	// Create a scanner to read the file line by line
	scanner := bufio.NewScanner(file)

	// Iterate over each line in the file
	for scanner.Scan() {
		line := scanner.Text() // Get the current line

		if strings.Contains(line, "ubox") {
			parts := strings.Fields(line)
			if len(parts) == 4 && parts[3] == "ubox" {
				i, _ := strconv.Atoi(parts[0])
				j, _ := strconv.Atoi(parts[1])
				val, _ := strconv.ParseFloat(parts[2], 64)
				bppMatrix[i-1][j-1] = val * val
				bppMatrix[j-1][i-1] = val * val
			}
		}
	}
	os.Remove(file_name)
	return bppMatrix 
}



func createTempFasta(sequence string) (string, string, error) {
	tempName := getRandomName()
	tempFasta, err := ioutil.TempFile("", "sequence_" + tempName)
	if err != nil {
		return "", "", fmt.Errorf("error creating temporary file: %w", err)
	}
	defer tempFasta.Close()
	
	// Placeholder for generating a unique name
	_, err = tempFasta.WriteString(fmt.Sprintf(">.sq%s\n%s", tempName, sequence))
	if err != nil {
		return "", "", fmt.Errorf("error writing to temporary file: %w", err)
	}
	return tempFasta.Name(), tempName, nil
}


func getRandomName() string {
	const chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
	result := make([]byte, 12)
	rand.Seed(time.Now().UnixNano())
	for i := range result {
		result[i] = chars[rand.Intn(len(chars))]
	}
	return string(result)
}

// findRegion finds the region with the largest score.
func findRegion(array1, array2 []float64, pos, minW int) (float64, int, int, float64) {
	minHW := int(minW / 2)
	rDis := int(len(array1) - pos)
	lDis := pos - 1
	score := 0.0
	pValue := 1.0
	LBLast := minHW
	RBLast := minHW

	scoreArray := make([][]float64, len(array1)+1)
	for i := range scoreArray {
		scoreArray[i] = make([]float64, len(array1)+1)
	}

	for LB := minHW; LB <= lDis; LB++ {
		for RB := minHW; RB <= rDis; RB++ {
			// Create copies of the original slices
			subsetLeft := make([]float64, len(array1))
			copy(subsetLeft, array1)

			subsetRight := make([]float64, len(array2))
			copy(subsetRight, array2)

			// Call the processing function with copies
			scoreNew, pValueNew := processSubsets(subsetLeft, subsetRight, LB, RB, pos)

			scoreArray[pos-LB-1][pos+RB] = scoreNew

			if scoreNew > score {
				score = scoreNew
				LBLast = LB
				RBLast = RB
				pValue = pValueNew
			}
		}
	}

	score = round(score, 3)
	return score, LBLast, RBLast, pValue
}

// New function to process the subsets
func processSubsets(left, right []float64, LB, RB, pos int) (float64, float64) {
	drapNew := drap(left, right, LB, RB, pos)
	pValueNew := onlinestats.KS(left[(pos-LB-1):(pos+RB)], right[(pos-LB-1):(pos+RB)])
	scoreNew := drapNew * (-math.Log10(pValueNew))
	return scoreNew, pValueNew
}

// drap calculates the median fold change.
func drap(one, two []float64, LB, RB, pos int) float64 {
	ppm1Seg := one[(pos-LB-1):(pos+RB)]
	ppm2Seg := two[(pos-LB-1):(pos+RB)]
	dis := getMedianFC(ppm1Seg, ppm2Seg)
	return dis
}

// round rounds the float to n decimal places.
func round(x float64, n int) float64 {
	pow := math.Pow(10, float64(n))
	return math.Round(x*pow) / pow
}

// getMedianFC calculates the median fold change.
func getMedianFC(seg1, seg2 []float64) float64 {
	// Calculate the median of both segments
	median1 := median(seg1)
	median2 := median(seg2)

	dis := math.Max(
        (median1 + 0.001) / (median2 + 0.001),
        (median2 + 0.001) / (median1 + 0.001),
    )
	return dis }

// median calculates the median of a slice.
func median(data []float64) float64 {
	sort.Float64s(data)
	n := len(data)
	if n%2 == 0 {
		return (data[n/2-1] + data[n/2]) / 2
	}
	return data[n/2]
}

func getSumMatrixCols(matrix [][]float64) []float64 {
    if len(matrix) == 0 {
        return nil // Handle empty matrix case
    }

    colSums := make([]float64, len(matrix[0])) // Use the number of columns
    for i := range matrix {
        for j := range matrix[i] { // Use matrix[i] for column access
            colSums[j] += matrix[i][j]
        }
    }

    // Round to 5 decimal places
    for k := range colSums {
        colSums[k] = math.Round(colSums[k]*100000000) / 100000000
    }

    return colSums
}

func getMutatedSequence(sequence string, mutation string) string {
	index, _ := strconv.Atoi(mutation[1 : len(mutation)-1])

	mutatedSequence := sequence[:index-1] + string(mutation[len(mutation)-1]) + sequence[index:]
	return mutatedSequence
}