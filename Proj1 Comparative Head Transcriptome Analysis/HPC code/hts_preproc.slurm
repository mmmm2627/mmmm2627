#!/bin/bash

#SBATCH --job-name=htstream_XX # Job name
#SBATCH -A XXX  ## account to charge
#SBATCH --nodes=1
#SBATCH --ntasks=9
#SBATCH --time=120
#SBATCH --mem-per-cpu=8G    # Memory pool for all cores (see also --mem-per-cpu)
#SBATCH -p standard               ## partition name
#SBATCH --array=1-11
#SBATCH --output=slurmout/htstream_%A_%a.out # File to which STDOUT will be written
#SBATCH --error=slurmout/htstream_%A_%a.err # File to which STDERR will be written
#SBATCH --mail-type=fail,end
#SBATCH --mail-user=email

source ~/miniconda3/bin/activate
conda activate Parsch

start=`date +%s`
echo $HOSTNAME
echo "My SLURM_ARRAY_TASK_ID: " $SLURM_ARRAY_TASK_ID

sample=`sed "${SLURM_ARRAY_TASK_ID}q;d" samples.txt`

inpath="00-RawData"
outpath="01-HTS_Preproc"
[[ -d ${outpath} ]] || mkdir ${outpath}
[[ -d ${outpath}/${sample} ]] || mkdir ${outpath}/${sample}

echo "SAMPLE: ${sample}"

#module load htstream/1.3.3

call="hts_Stats -L ${outpath}/${sample}/${sample}.json -N 'initial stats' \
          -1 ${inpath}/${sample}/${sample}_R1.fastq \
          -2 ${inpath}/${sample}/${sample}_R2.fastq | \
      hts_SeqScreener -A ${outpath}/${sample}/${sample}.json -N 'screen phix' | \
      hts_SeqScreener -A ${outpath}/${sample}/${sample}.json -N 'count the number of rRNA reads'\
          -r -s ./References/drosophila_rrna.fasta | \
      hts_SuperDeduper -A ${outpath}/${sample}/${sample}.json -N 'remove PCR duplicates' | \
      hts_AdapterTrimmer -A ${outpath}/${sample}/${sample}.json -N 'trim adapters' | \
      hts_PolyATTrim -A ${outpath}/${sample}/${sample}.json -N 'remove polyAT' | \
      hts_NTrimmer -A ${outpath}/${sample}/${sample}.json -N 'remove any remaining N characters' | \
      hts_QWindowTrim -A ${outpath}/${sample}/${sample}.json -N 'quality trim the ends of reads' | \
      hts_LengthFilter -A ${outpath}/${sample}/${sample}.json -N 'remove reads < 50bp' \
          -n -m 50 | \
      hts_Stats -A ${outpath}/${sample}/${sample}.json -N 'final stats' \
          -f ${outpath}/${sample}/${sample}"

echo $call
eval $call

end=`date +%s`
runtime=$((end-start))
echo $runtime

conda deactivate
conda deactivate
