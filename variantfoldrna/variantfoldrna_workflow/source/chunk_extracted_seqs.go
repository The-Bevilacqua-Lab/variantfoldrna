package main

import (
	"bufio"
	"flag"
	"fmt"
	"os"
	"path/filepath"
)

func splitFileByLine(filename string, n int, nullFlag bool, outputDir string) error {
	file, err := os.Open(filename)
	if err != nil {
		return err
	}
	defer file.Close()

	scanner := bufio.NewScanner(file)
	lineCount := 0
	for scanner.Scan() {
		lineCount++
	}
	if err := scanner.Err(); err != nil {
		return err
	}

	chunkSize := lineCount / n
	remainder := lineCount % n

	file.Seek(0, 0)
	for i := 0; i < n; i++ {
		var chunkFileName string
		if nullFlag {
			chunkFileName = filepath.Join(outputDir, "extracted_sequences_null", fmt.Sprintf("extracted_seqs_null_unique_chunk_%d.txt", i+1))
		} else {
			chunkFileName = filepath.Join(outputDir, "extracted_seqs_chunks", fmt.Sprintf("extracted_flank_snp_%d.txt", i+1))
		}

		chunkFile, err := os.Create(chunkFileName)
		if err != nil {
			return err
		}
		defer chunkFile.Close()

		chunkWriter := bufio.NewWriter(chunkFile)
		linesToWrite := chunkSize
		if i < remainder {
			linesToWrite++
		}

		for j := 0; j < linesToWrite; j++ {
			scanner.Scan()
			chunkWriter.WriteString(scanner.Text() + "\n")
		}
		chunkWriter.Flush()
	}

	return nil
}

func main() {
	inputFile := flag.String("input", "", "input file")
	outputDir := flag.String("dir", "", "working directory")
	nullFlag := flag.Bool("null", false, "null file")
	chunkTotal := flag.Int("chunk-total", 0, "The number of files to chop the input into")
	flag.Parse()

	if *inputFile == "" || *outputDir == "" || *chunkTotal == 0 {
		flag.PrintDefaults()
		os.Exit(1)
	}

	// Make a directory to store the chunks
	chunksDir := filepath.Join(*outputDir, "extracted_seqs_chunks")
	if err := os.MkdirAll(chunksDir, os.ModePerm); err != nil {
		fmt.Println("Error creating chunks directory:", err)
		os.Exit(1)
	}

	nullDir := filepath.Join(*outputDir, "extracted_sequences_null")
	if err := os.MkdirAll(nullDir, os.ModePerm); err != nil {
		fmt.Println("Error creating null directory:", err)
		os.Exit(1)
	}

	if err := splitFileByLine(*inputFile, *chunkTotal, *nullFlag, *outputDir); err != nil {
		fmt.Println("Error splitting file:", err)
		os.Exit(1)
	}

	fmt.Println("File split successfully.")
}
