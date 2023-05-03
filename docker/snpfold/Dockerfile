##########################################################################################
# Dockerfile for RNAsnp
# 
# Author: Kobie Kirven
#########################################################################################

FROM nciccbr/ccbr_ubuntu_base_20.04:v2.1

RUN wget https://www.ncbi.nlm.nih.gov/CBBresearch/Przytycka/software/remurna/remuRNA.zip && \
    unzip remuRNA.zip && \
    cd remuRNA && \
    make

ENV PATH="/data2/remuRNA:${PATH}"