#!/bin/bash
#SBATCH --job-name=DL_NCU
#SBATCH -p standard
#SBATCH --nodes=1
#SBATCH --ntasks=4
#SBATCH --time=72:00:00
#SBATCH --mem-per-cpu=32G
#SBATCH --output=/path/download_%A_%a.out
#SBATCH --error=/path/download_%A_%a.err
#SBATCH --mail-type=ALL
#SBATCH --mail-user=email


#change to directory you want the files downloaded into
#cd /share/crsp/lab/jranz/share/SequencingData/NCU_Dele_RNAseq

module load sra-tools/3.0.0

prefetch --option-file sra-list_.txt

for data in SRR*; do fastq-dump --split-files -O $data $data/$data.sra;  done
