# LRModel
Binary classifier to predict regulatory elements using a simple logistic regression based model.

## INTRODUCTION

What's fascinating about the human genome is that it only contains ~21,000 protein coding genes, yet there are ~2 million DNA sequences that control the expression of those genes.
Out of the 2 million anywhere from 40,000 to 200,000 are often expressed in one of the cell types. What are some features that help you identify regulatory elements? Well it turns out
there are proteins called transcription factors that bind short ~6 bp sequences (motifs) in these regulatory regions of our DNA. After several years of experimental and computational approaches 
we know the motifs for ~1200 out of 1639 transcription factors in the genome. We can use features derived from these motifs to build simple predictive models for regulatory elements.

## Model explanation

Motifs are represented as position weight matrices (PWMs) which can be downloaded from databases such as CIS-BP or JASPAR. The general idea of the model is to have positive sequences (regulatory elements) 
and negative sequences (not regulatory elements), use TF motifs to obtain features and then use a simple logistic regression based model to learn from those features to discriminate between
the two classes. 

### Obtaining positive and negative data

For positive data you can grab DHS sites (regions of open chromatin that are essentially a proxy for identifying regulatory elements) in a particular cell type from ENCODE or Roadmap Epigenome consortiums. 
For negative data you have several options. One way is to generate a dinucleotide shuffled positive set, which can be easily done using the fasta-dinucleotide-shuffle-py3.py script available via https://meme-suite.org/meme/doc/fasta-dinucleotide-shuffle.html. 
Another option is to find random regions in the genome that do not overlap with your positive sequences and have matching GC content and repeat-element content. This is little tricky but the genNullSeqs function from the gkmSVM R package is a good way to generate
this type of a negative set https://cran.r-project.org/web/packages/gkmSVM/gkmSVM.pdf

### Obtaining PWMs 

As mentioned previously, one could obtain a large set of motif PWMs from CIS-BP or JASPAR. The CIS-BP IDs for PWMs that I used to train the model are in the additional file 4 from my paper https://genomebiology.biomedcentral.com/articles/10.1186/s13059-021-02503-y#Sec17

### Scanning PWMs in positive and negative sequences

To extract features first you need to scan the positive and negative sequences for features. I like to use the MOODS tool https://github.com/jhkorhonen/MOODS for this task. To run MOODS you need 2 things:
1. Folder with your PWMs 
2. Your fasta sequence file 

Run MOODS twice, one for the positive fasta file and one for the negative fasta file. If you use the --batch feature in MOODS, it allows you to scan several sequences with several PWMs pretty quickly on your own laptop.

`python moods-dna.py --batch -S /PWMFolder/*.txt -s Positive.fa -p 0.0001 -o PositiveSequencesHits.txt`

`python moods-dna.py --batch -S /PWMFolder/*.txt -s Negative.fa -p 0.0001 -o NegativeSequencesHits.txt`

### Extracting features from MOODS output

MOODS represents all the hits as individual rows in its output file. For the logistic regression model, one would have to turn MOODS output into a matrix (# of sequences * # of features). The features can be motif hits, highest motif score, or average motif score.
To run the FeatureExtractor script, you first need to compute the minimum and maximum scores for each of your PWMs (just add up the max values in each column for max and opposite for minimum). This allows you to compute relative scores ((hit score - min score)/(max score - min score)) for each of your hits. I created a minmax.txt file for several PWMs in CIS-BP. 

#### Motif hits as features

To compute matrix of motif hits, simply run the below code

`python GenerateMotifHitMatrix.py --MaxMinFile minmax.txt --MoodsOutput PositiveSequencesHits.txt --SequenceClass 1 --output PositiveSequencesHitsMatrix.txt`

`python GenerateMotifHitMatrix.py --MaxMinFile minmax.txt --MoodsOutput NegativeSequencesHits.txt --SequenceClass 0 --output NegativeSequencesHitsMatrix.txt`

### Run Logistic Regression Training model 

To run the logistic regression training model, you need to provide the positive feature matrix, negative feature matrix, random seed # to pick chromosomes for training, number of chromosomes used for training and where to store the trained model. 
The code also prints out the AUROC value. 

`python LogRegTrain.py --Positive PositiveSequencesHitsMatrix.txt --Negative NegativeSequencesHitsMatrix.txt --RandomSeed 6 --chrTrainNum 16 --output logregTrain.sav`


