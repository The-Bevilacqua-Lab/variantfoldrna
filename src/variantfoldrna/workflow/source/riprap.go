// Go implementation of the RipRap algorithm
// Original python code was obtained from

package main

import (
	// "flag"
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
	// "github.com/montanaflynn/stats"
	"github.com/dgryski/go-onlinestats"
	"time"
	// "sync"
	// "testing"
)
func main() {
	// Example usage
	// ppv1 := []float64{0.0, 0.0, 0.0, 1.0, 2.0, 3.0, 0.0, 0.0, 0.0, 1.0, 2.0, 3.0,0.0, 0.0, 0.0, 1.0, 2.0, 3.0, 0.0, 0.0, 0.0, 1.0, 2.0, 3.0, 0.0, 0.0, 0.0, 1.0, 2.0, 3.0, 0.0, 0.0, 0.0, 1.0, 2.0, 3.0,0.0, 0.0, 0.0, 1.0, 2.0, 3.0, 0.0, 0.0, 0.0, 1.0, 2.0, 3.0}
	// ppv2 := []float64{0.0, 0.0, 0.0, 1.0, 2.0, 3.0, 0.0, 0.0, 0.0, 1.0, 2.0, 3.0, 1.1,1.2,1.3,1.5, 2.5, 3.5,0.0, 0.0, 0.0, 1.0, 2.0, 3.0, 0.0, 0.0, 0.0, 1.0, 2.0, 3.0, 0.0, 0.0, 0.0, 1.0, 2.0, 3.0, 1.1,1.2,1.3,1.5, 2.5, 3.5,0.0, 0.0, 0.0, 1.0, 2.0, 3.0}
	
	bppMatrix, err := getBPPMatrix("AUCGCGAUUAUUGGAAUCGAUCGGGAUAUCGCGAUUAUUGGAAUCGAUCGGGAUAUCGCGAUUAUUGGAAUCGAUCGGGAUAUCGCGAUUAUUGGAAUCGAUCGGGAU", "37.0")
	bppMatrixMut, err := getBPPMatrix("AUCGCGUUUAUUGGAAUCGAUCGGGAUAUCGCGAUUAUUGGAAUCGAUCGGGAUAUCGCGAUUAUUGGAAUCGAUCGGGAUAUCGCGAUUAUUGGAAUCGAUCGGGAU", "37.0")
	colSums := getSumMatrixCols(bppMatrix)
	fmt.Println(colSums)
	colSumsMut := getSumMatrixCols(bppMatrixMut)
	
	if err != nil {
			fmt.Println("Error converting position to integer:")
			os.Exit(1)
		}
	pos := 7
	minW := 3

	score, LBLast, RBLast, pValue := findRegion(colSums, colSumsMut, pos, minW)
	fmt.Println("Score:", score, "LB:", pos - LBLast, "RB:", pos+RBLast, "pValue:", pValue)
}
// func main() {

// 	// Read in the command line inputs 
// 	seq := flag.String("seq", "", "Sequence")
// 	mutation := flag.String("mut", "", "Mutation")
// 	temp := flag.String("T", "", "Temperature")
// 	flag.Parse()

// 	// Check to make sure that we have a value for each of the inputs
// 	if *seq == "" || *mutation == "" || *temp == "" {
// 		flag.PrintDefaults()
// 		os.Exit(1)
// 	}

// 	// Check to make sure there are no N's in the sequence 
// 	if strings.Contains(*seq, "N") {
// 		fmt.Println("N is in the sequence")
// 		os.Exit(1)
// 	}

// 	// Get the reference allele 
// 	ref := string((*mutation)[0])

// 	// Get the position of the mutation
// 	pos, err := strconv.Atoi((*mutation)[1:len(*mutation)-1])

// 	// Check to see if there was an error when converting the mutation
// 	// position to an integer
// 	if err != nil {
// 		fmt.Println("Error converting position to integer:", err)
// 		os.Exit(1)
// 	}

// 	if string((*seq)[pos-1]) != ref {
// 		fmt.Println("Reference allele does not match sequence at position", pos)
// 		os.Exit(1)
// 	}

// 	if strings.Contains(*mutation, "N") {
// 		fmt.Println("N is in the mutation")
// 		os.Exit(1)
// 	}

// 	// Get the base-pairing probability matrix, the 
// 	// freeEnergy, and the ensembleDiversity for the REF and ALT alleles
// 	bppMatrix, freeEnergy, ensembleDiversity, nil := getBPPMatrix(*seq, *temp)
// 	bppMatrixMut, freeEnergyMut, ensembleDiversityMut, nil := getBPPMatrix(getMutatedSequence(*seq, *mutation), *temp)

// 	colSums := getSumMatrixCols(bppMatrix)
// 	colSumsMut := getSumMatrixCols(bppMatrixMut)

// 	pearson, err := stats.Pearson(colSums, colSumsMut)
// 	if err != nil {
// 		fmt.Println("Error calculating Pearson correlation coefficient:", err)
// 		os.Exit(1)
// 	}

// 	fmt.Println(fmt.Sprintf("%s,%s,%s,%s,%f", freeEnergy, ensembleDiversity, freeEnergyMut, ensembleDiversityMut, pearson))
// }


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

	// if err != nil {
	// 	return nil, "", "", fmt.Errorf("error extracting ensemble info: %w", err)
	// }

	// Parse output to extract base pair probability matrix
	bppMatrix  := parseOutput(".sq" + name + "_dp.ps", sequence)
	// if err != nil {
	// 	return nil, "", "", fmt.Errorf("error parsing output: %w", err)
	// }

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
func findRegion(ppv1, ppv2 []float64, pos, minW int) (float64, int, int, float64) {
	minHW := int(minW / 2)
	rDis := int(len(ppv1) - pos)

	lDis := pos - 1
	score := 0.0
	pValue := 1.0
	LBLast := minHW
	RBLast := minHW
	
	scoreArray := make([][]float64, len(ppv1)+1)
	for i := range scoreArray {
		scoreArray[i] = make([]float64, len(ppv1)+1)
	}
	
	for LB := minHW; LB <= lDis; LB++ {
		for RB := minHW; RB <= rDis; RB++ {
					// Create a destination slice with the same length
			subsetLeft := make([]float64, len(ppv1))
			// Use copy to copy elements from original to dest
			copy(subsetLeft, ppv1)

			subsetRight := make([]float64, len(ppv2))
			// Use copy to copy elements from original to dest
			copy(subsetRight, ppv2)

			pValueNew := onlinestats.KS(subsetLeft[(pos-LB-1):(pos+RB)], subsetRight[(pos-LB-1):(pos+RB)])
			drapNew := drap(subsetLeft,subsetRight, LB, RB, pos)
			
			scoreNew := drapNew* (-math.Log10(pValueNew))
			
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

// drap calculates the median fold change.
func drap(ppm1, ppm2 []float64, LB, RB, pos int) float64 {
	ppm1Seg := ppm1[(pos-LB-1):(pos+RB)]
	ppm2Seg := ppm2[(pos-LB-1):(pos+RB)]
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
	// if median2 == 0 {
	// 	return 0 // Prevent division by zero
	// }

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