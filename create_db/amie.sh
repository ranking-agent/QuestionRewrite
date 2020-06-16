#!/bin/bash

#SBATCH -N 1
#SBATCH -c 4
#SBATCH --array=1-750
#SBATCH --mem-per-cpu=8000
#SBATCH -t 72:00:00
#SBATCH -o logs/%A_%a.out
#SBATCH -e logs/%A_%a.err

echo `hostname`

wdir=/projects/sequence_analysis/vol3/bizon/amie
cd $wdir

pred=`head -n $SLURM_ARRAY_TASK_ID preds | tail -n 1 | awk '{print $1}'`
echo $pred

onamev="${pred//<}"
oname="${onamev//>}"
echo $oname

#java -Xmx8g -jar amie_plus.jar -nc 4 -minpca 0 -minhc 0 -htr $pred amie_input_all > outputs/$pred
#java -Xmx8g -jar amie_plus.jar -nc 4 -minpca 0.0001 -minhc 0.0001 -htr $pred amie_input_all > outputs_b/$pred
#java -Xmx8g -jar amie_plus.jar -nc 4 -minpca 0.001 -minhc 0.001 -htr $pred amie_input_all > outputs_c/$pred
#java -Xmx8g -jar amie_plus.jar -nc 4 -minpca 0.01 -minhc 0.01 -htr $pred amie_input_all > outputs_d/$pred
java -Xmx8g -jar amie_plus.jar -nc 4 -minpca 0.01 -minhc 0.01 -htr $pred amie_input_all > output_fast/$oname
