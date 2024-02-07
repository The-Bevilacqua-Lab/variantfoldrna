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
)

func main() {
	seq := flag.String("seq", "", "Sequence")
	mutation := flag.String("mut", "", "Mutation")
	temp := flag.String("T", "", "Temperature")
	flag.Parse()

	if *seq == "" || *mutation == "" || *temp == "" {
		flag.PrintDefaults()
		os.Exit(1)
	}

	if strings.Contains(*seq, "N") {
		fmt.Println("N is in the sequence")
		os.Exit(1)
	}

	if strings.Contains(*mutation, "N") {
		fmt.Println("N is in the mutation")
		os.Exit(1)
	}

	bppMatrix := getBPPMatrix(*seq, *temp)
	bppMatrixMut := getBPPMatrix(getMutatedSequence(*seq, *mutation), *temp)

	colSums := getSumMatrixCols(bppMatrix)
	colSumsMut := getSumMatrixCols(bppMatrixMut)

	pearson := getPearson(colSums, colSumsMut)

	fmt.Println(pearson)
}

func getBPPMatrix(sequence string, temp string) [][]float64 {
	tempFasta, name := getTempFasta(sequence)
	defer os.Remove(tempFasta)

	cmd := exec.Command("RNAfold", "-p", "--noPS", "-i", tempFasta, "-T", temp)
	_, err := cmd.CombinedOutput()
	if err != nil {
		fmt.Println("Error running RNAfold:", err)
		os.Exit(1)
	}

	bppMatrix := make([][]float64, len(sequence))
	for i := range bppMatrix {
		bppMatrix[i] = make([]float64, len(sequence))
	}

	file, err := os.Open(".sq" + name + "_dp.ps")

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

	os.Remove(".sq" + name + "_dp.ps")
	return bppMatrix
}

func getTempFasta(sequence string ) (string, string) {
	tempFasta, err := ioutil.TempFile("", "sequence_")
	if err != nil {
		fmt.Println("Error creating temporary file:", err)
		os.Exit(1)
	}
	defer tempFasta.Close()
	
	temp_name := getRandomName()
	_, err = tempFasta.WriteString(fmt.Sprintf(">.sq%s\n%s", temp_name, sequence))
	if err != nil {
		fmt.Println("Error writing to temporary file:", err)
		os.Exit(1)
	}

	return tempFasta.Name(), temp_name
}


func getRandomName() string {
	const chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
	result := make([]byte, 6)
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


func getPearson(list1 []float64, list2 []float64) float64 {
	n := float64(len(list1))
	if n != float64(len(list2)) {
		fmt.Println("Lists have different lengths")
		os.Exit(1)
	}

	var sumXY, sumX, sumY, sumX2, sumY2 float64
	for i := 0; i < len(list1); i++ {
		sumXY += list1[i] * list2[i]
		sumX += list1[i]
		sumY += list2[i]
		sumX2 += math.Pow(list1[i], 2)
		sumY2 += math.Pow(list2[i], 2)
	}

	numerator := n*sumXY - sumX*sumY
	denominator := math.Sqrt((n*sumX2 - math.Pow(sumX, 2)) * (n*sumY2 - math.Pow(sumY, 2)))

	return roundFloat(numerator/denominator, 3)
}
