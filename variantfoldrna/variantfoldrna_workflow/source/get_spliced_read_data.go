////////////////////////////////////////////////////////////////////////////////
// Extract the flanking sequence surrounding the SNP
//
// Author: Kobie Kirven
////////////////////////////////////////////////////////////////////////////////

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

func main() {
	// Parse command-line flags
	vcfPath := flag.String("vcf", "", "VCF File")
	refSeqsPath := flag.String("ref-seqs", "", "Reference Genome")
	flankLength := flag.Int("flank", 0, "SNP flanking length")
	cdsPosPath := flag.String("cds-pos", "", "CDS start")
	gffreadPath := flag.String("gffread", "", "Gffread Table")
	outputPath := flag.String("o", "", "Output File")
	transcriptPrefixFile := flag.String("transcript-prefix", "", "Transcript Prefix")
	flag.Parse()

	// Check if required flags are provided
	if *vcfPath == "" || *refSeqsPath == "" || *flankLength == 0 || *cdsPosPath == "" || *gffreadPath == "" || *outputPath == "" || *transcriptPrefixFile == "" {
		flag.PrintDefaults()
		os.Exit(1)
	}

	// Open the output files
	outputFile, err := os.Create(*outputPath)
	if err != nil {
		fmt.Println("Error creating output file:", err)
		os.Exit(1)
	}
	defer outputFile.Close()

	// Read in the transcript prefix
	transcriptPrefixF, err := os.Open(*transcriptPrefixFile)
	if err != nil {
		fmt.Println("Error opening transcript prefix file:", err)
		os.Exit(1)
	}
	defer transcriptPrefixF.Close()

	// Use the first line in the file as the prefix
	scanner1 := bufio.NewScanner(transcriptPrefixF)
	scanner1.Scan()
	transcriptPrefix := scanner1.Text()

	// Create a file for if the REF allele does not match the reference genome
	noMatchFile, err := os.Create(strings.TrimSuffix(*outputPath, ".txt") + "_no_match.txt")
	if err != nil {
		fmt.Println("Error creating no match file:", err)
		os.Exit(1)
	}
	defer noMatchFile.Close()

	// Read in the file with the VEP predictions
	vcfFile, err := os.Open(*vcfPath)
	if err != nil {
		fmt.Println("Error opening VCF file:", err)
		os.Exit(1)
	}
	defer vcfFile.Close()

	scanner := bufio.NewScanner(vcfFile)
	for scanner.Scan() {
		line := scanner.Text()
		if strings.HasPrefix(line, "#") {
			continue // Skip header lines
		}

		// Split the line by tabs
		fields := strings.Split(line, "\t")
		
		// Make sure we are not working with an insertion or deletion
		if len(fields[1]) > 1 || len(fields[2]) > 1 {
			continue
		}

		// Get the strand of the transcript
		strand, err := strconv.Atoi(fields[7])

		if err != nil {
			fmt.Println("Error parsing strand:", err)
			continue
		}
		

		// Get the sequence from the reference genome
		seq := getCDNA(fields[4], *flankLength, *refSeqsPath, fields[5], strand, transcriptPrefix)

		
		// Check if we got a sequence
		if seq == "" {
			continue
		}
		if seq == "" {
			noMatchFile.WriteString(line + "\n")
			continue
		}

		// The sequence is outputted in FASTA format, so we need to remove the header
		sequence := strings.Split(seq, "\n")[1:]

		// Join the sequence which is now in a list
		joinedSeq := strings.Join(sequence, "")

		if strings.Contains(joinedSeq, "N"){
			continue 
		}

		// Chck to see if the extracted sequence is less than twice the flank length + 1
		if len(joinedSeq) < 2**flankLength+1 {
			continue
		}

		// Get the reference and alternative alleles
		refAllele := fields[1]
		altAllele := fields[2]

		// Get the complement of the reference and alternative alleles if the strand is negative
		if strand == -1 {
			refAllele = getComplement(refAllele)
			altAllele = getComplement(altAllele)

		}

		// Split the chrom position by the ':'
		chromPos := strings.Split(fields[0], ":")

		// Get whether the Ref allele matches what is in the genome
		refMatch := "MATCHED_ALT"

		if string(joinedSeq[*flankLength]) == refAllele {
			refMatch = "MATCHED_REF"
		} else if string(joinedSeq[*flankLength]) != altAllele {
			refMatch = "NO_MATCH"
		}

		if refAllele == "T" {
			refAllele = "U"
		}

		if altAllele == "T" {
			altAllele = "U"
		}

		// Write the information to the output file
		_, err = fmt.Fprintf(outputFile, "%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n", chromPos[0], chromPos[1], fields[5], refAllele, altAllele, joinedSeq[:*flankLength], joinedSeq[*flankLength+1:], fields[4], refMatch, fields[3], fields[7])
		if err != nil {
			fmt.Println("Error writing to output file:", err)
		}
	}

	if err := scanner.Err(); err != nil {
		fmt.Println("Error scanning VCF file:", err)
		os.Exit(1)
	}
}

func getCDNA(transcriptID string, flankLength int, seqPath string, cdsPos string, strand int, transcriptPrefix string) string {
	pos, err := strconv.Atoi(cdsPos)

	if cdsPos == "-" {
		return ""
	} 
	
	if len(strings.Split(cdsPos, "-")) > 1 {
		return ""
	}
	

	if err != nil {
		fmt.Println("Error parsing CDS position:", err)
		return ""
	}
	if pos-flankLength < 1 {
		return ""
	}

	// print("samtools", "faidx", seqPath, fmt.Sprintf("transcript:%s:%d-%d", transcriptID, pos-flankLength, pos+flankLength))
	// println(fmt.Sprintf("%s:%s:%d-%d", transcriptPrefix, transcriptID, pos-flankLength, pos+flankLength))
	// print(fmt.Sprintf("%s:%s:%d-%d", transcriptPrefix, transcriptID, pos-flankLength, pos+flankLength))
	cmd := exec.Command("samtools", "faidx", seqPath, fmt.Sprintf("%s%s:%d-%d", transcriptPrefix, transcriptID, pos-flankLength, pos+flankLength))
	output, _ := cmd.CombinedOutput()

	if len(output) == 1 {
		return ""
	}

	// The sequence is outputted in FASTA format, so we need to remove the header
	sequence := strings.Split(string(output), "\n")[1:]

	// Join the sequence which is now in a list
	joinedSeq := strings.Join(sequence, "")

	// Chck to see if the extracted sequence is less than twice the flank length + 1
	if len(joinedSeq) < (2*flankLength+1) {
		return ""
	}

	return string(output)


}

func getComplement(allele string) string {
	complement := strings.NewReplacer("A", "T", "T", "A", "C", "G", "G", "C", "N", "N")
	return complement.Replace(allele)
}
