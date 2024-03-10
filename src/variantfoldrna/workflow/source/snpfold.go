// Go implementation of the SNPfold algorithm
// Original python code was obtained from https://github.com/Halvee/SNPfold

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
	"github.com/montanaflynn/stats"
	"time"
	// "sync"
	// "testing"
)

func main() {

	// Read in the command line inputs 
	seq := flag.String("seq", "", "Sequence")
	mutation := flag.String("mut", "", "Mutation")
	temp := flag.String("T", "", "Temperature")
	flag.Parse()

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

	// Get the base-pairing probability matrix, the 
	// freeEnergy, and the ensembleDiversity for the REF and ALT alleles
	bppMatrix, freeEnergy, ensembleDiversity, nil := getBPPMatrix(*seq, *temp)
	bppMatrixMut, freeEnergyMut, ensembleDiversityMut, nil := getBPPMatrix(getMutatedSequence(*seq, *mutation), *temp)

	colSums := getSumMatrixCols(bppMatrix)
	colSumsMut := getSumMatrixCols(bppMatrixMut)

	pearson, err := stats.Pearson(colSums, colSumsMut)
	if err != nil {
		fmt.Println("Error calculating Pearson correlation coefficient:", err)
		os.Exit(1)
	}

	fmt.Println(fmt.Sprintf("%s,%s,%s,%s,%f", freeEnergy, ensembleDiversity, freeEnergyMut, ensembleDiversityMut, pearson))
}


func getBPPMatrix(sequence string, temp string) ([][]float64, string, string, error) {
	// Create a temporary FASTA file with the given sequence
	tempFasta, name, err := createTempFasta(sequence)
	if err != nil {
		return nil, "", "", err
	}
	defer os.Remove(tempFasta) // Remove the temporary FASTA file when done

	// Execute RNAfold command
	output, err := exec.Command("RNAfold", "-p", "--noPS", "-i", tempFasta, "-T", temp).Output()
	if err != nil {
		return nil, "", "", fmt.Errorf("error running RNAfold: %w", err)
	}

	// Extract free energy of the ensemble and ensemble diversity
	freeEnergy, ensembleDiversity := extractEnsembleInfo(string(output))
	// if err != nil {
	// 	return nil, "", "", fmt.Errorf("error extracting ensemble info: %w", err)
	// }

	// Parse output to extract base pair probability matrix
	bppMatrix  := parseOutput(".sq" + name + "_dp.ps", sequence)
	// if err != nil {
	// 	return nil, "", "", fmt.Errorf("error parsing output: %w", err)
	// }

	return bppMatrix, freeEnergy, ensembleDiversity, nil
}

func extractEnsembleInfo(outputStr string) (string, string) {

	// Split the output by newline characters
	lines := strings.Split(outputStr, "\n")

	// Extract free energy of the ensemble
	freeEnergyLine := lines[2]
	freeEnergy := strings.Split(freeEnergyLine, " ") // Extract the part after '('
	freeEnergyLength := len(freeEnergy)
	freeEnergyEle := freeEnergy[freeEnergyLength-1] // Extract the last element
	freeEnergyEle = strings.TrimRight(freeEnergyEle, ") ")    // Remove trailing ')' and space
	freeEnergyEle = strings.TrimLeft(freeEnergyEle, "( ") 
	// Extract ensemble diversity
	ensembleDiversityLine := lines[5]
	ensembleDiversity := strings.Split(ensembleDiversityLine, ";")[1]
	ensembleDiversity = strings.Split(ensembleDiversityLine, " ")[10] // Extract the part after ';'
	ensembleDiversity = strings.TrimSpace(ensembleDiversity)

	return freeEnergyEle, ensembleDiversity

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

func getMutatedSequence(sequence string, mutation string) string {
	index, _ := strconv.Atoi(mutation[1 : len(mutation)-1])

	mutatedSequence := sequence[:index-1] + string(mutation[len(mutation)-1]) + sequence[index:]
	return mutatedSequence
}

func getSumMatrixCols(matrix [][]float64) []float64 {
	colSums := make([]float64, len(matrix))
	for i := range matrix {
		for j := range matrix {
			colSums[j] += matrix[i][j]
		}
	}
	return colSums
}

func roundFloat(val float64, precision uint) float64 {
    ratio := math.Pow(10, float64(precision))
    return math.Round(val*ratio) / ratio
}
