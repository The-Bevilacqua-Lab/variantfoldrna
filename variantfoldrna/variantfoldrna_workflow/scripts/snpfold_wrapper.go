package main

import (
	"bufio"
	"flag"
	"fmt"
	"os"
	"os/exec"
	"strconv"
	"strings"
)

func transcribeRNA(seq string) string {
	return strings.ReplaceAll(seq, "T", "U")
}

func changeNucleotide(nuc byte) byte {
	nucDict := map[byte]byte{'A': 'U', 'T': 'A', 'G': 'C', 'C': 'G'}
	return nucDict[nuc]
}

func runSNPFold(seq, path, temp, mutation string) float64 {
	cmd := exec.Command(fmt.Sprintf("%s/snpfold", path), "-T", temp, "-seq", seq, "-mut", mutation)
	output, err := cmd.Output()
	if err != nil {
		fmt.Println("Error:", err)
		return -1
	}

	result, err := strconv.ParseFloat(strings.TrimSpace(string(output)), 64)
	if err != nil {
		fmt.Println("Error parsing result:", err)
		return -1
	}

	return result
}

func main() {
	// Parse command line arguments
	inFile := flag.String("i", "", "Input File")
	output := flag.String("o", "", "Output")
	flank := flag.Int("flank", 0, "Flanking length")
	temp := flag.String("temp", "", "Temp")
	path := flag.String("path", "", "Path")
	flag.Parse()

	// Get the path to the current directory
	// path, err := os.Getwd()
	// if err != nil {
	// 	fmt.Println("Error getting current directory:", err)
	// 	return
	// }

	// Open input and output files
	inFilePtr, err := os.Open(*inFile)
	if err != nil {
		fmt.Println("Error opening input file:", err)
		return
	}
	defer inFilePtr.Close()

	outFilePtr, err := os.Create(*output)
	if err != nil {
		fmt.Println("Error creating output file:", err)
		return
	}
	defer outFilePtr.Close()

	// Open error file
	errorFilePtr, err := os.Create(strings.TrimSuffix(*output, ".txt") + "_error.txt")
	if err != nil {
		fmt.Println("Error creating error file:", err)
		return
	}
	defer errorFilePtr.Close()

	scanner := bufio.NewScanner(inFilePtr)
	for scanner.Scan() {
		line := scanner.Text()

		// Skip header lines
		if !strings.HasPrefix(line, "#") {
			fields := strings.Fields(line)

			// Check for indels
			if len(fields[3]) != 1 || len(fields[4]) != 1 {
				continue
			}

			// Transcribe RNA and adjust nucleotides
			seq := fields[5] + fields[3] + fields[6]
			seq = transcribeRNA(seq)
			mutation := string(fields[3]) + strconv.Itoa(int(*flank)+1) + string(fields[4])

			// Run SNPfold
			result := runSNPFold(seq, *path, *temp, mutation)

			// Write result to output file
			_, err := fmt.Fprintf(outFilePtr, "%s\t%f\n", line, result)
			if err != nil {
				fmt.Println("Error writing to output file:", err)
				return
			}
		}
	}

	if err := scanner.Err(); err != nil {
		fmt.Println("Error reading input file:", err)
	}

	fmt.Println("Process complete.")
}
