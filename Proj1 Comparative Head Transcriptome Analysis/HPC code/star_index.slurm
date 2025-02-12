#!/bin/bash

#SBATCH --job-name=star_index_MU # Job name
#SBATCH -A XX_LAB              ## account to charge
#SBATCH --nodes=1
#SBATCH --ntasks=16
#SBATCH --time=120
#SBATCH --mem=40000 # Memory pool for all cores (see also --mem-per-cpu)
#SBATCH -p standard               ## partition name
#SBATCH --output=slurmout/star-index_%A.out # File to which STDOUT will be written
#SBATCH --error=slurmout/star-index_%A.err # File to which STDERR will be written
#SBATCH --mail-type=fail,end
#SBATCH --mail-user=email

source ~/miniconda3/bin/activate
conda activate Parsch

start=`date +%s`
echo $HOSTNAME

outpath="References"
mkdir -p ${outpath}

cd ${outpath}

#wget https://ftp.ebi.ac.uk/pub/databases/gencode/Gencode_mouse/release_M29/GRCm39.primary_assembly.genome.fa.gz
#gunzip dmel-all-chromosome-r6.47.fasta.gz
#FASTA="../GRCm39.primary_assembly.genome.fa"
FASTA="/path/to/fasta/file/dmel-all-chromosome-r6.47.fasta"

#wget https://ftp.ebi.ac.uk/pub/databases/gencode/Gencode_mouse/release_M29/gencode.vM29.primary_assembly.annotation.gtf.gz
#gunzip dmel-all-r6.47.gtf.gz
#GTF="../gencode.vM29.primary_assembly.annotation.gtf"
GTF="/path/to/fasta/file/dmel-all-r6.47.gtf"

#mkdir star.overlap100.dmel-all
cd star.overlap100.dmel-all

#module load star

call="STAR
    --runThreadN ${SLURM_NTASKS} \
    --runMode genomeGenerate \
    --genomeDir . \
    --genomeFastaFiles ${FASTA} \
    --sjdbGTFfile ${GTF} \
    --sjdbOverhang 100 \
    --genomeSAindexNbases 12"

echo $call
eval $call

end=`date +%s`
runtime=$((end-start))
echo $runtime

conda deactivate
conda deactivate
