rule scramble_fasta:
    input:
        f"{config['working_directory']}/{config['out_name']}/temp/extracted_sequences/extracted_seqs_{{i}}.txt"
    output:
        f"{config['working_directory']}/{config['out_name']}/temp/extracted_sequences/shuffled_seqs_{{i}}.txt"
    conda:
        "workflow/envs/scramble.yaml"
    shell:
        "python3 workflow/scripts/scramble.py -seq {input} -out {output}"