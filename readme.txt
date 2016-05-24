Instructions to run the program:

python calculatebleu.py /path/to/candidate /path/to/reference

You can test your program by running it on the following candidate and translation files, and comparing the result to the true BLEU score.

Language	Candidate		Reference			BLEU score
German		candidate-1.txt	reference-1.txt		0.151184476557
Greek		candidate-2.txt	reference-2.txt		0.0976570839819
Portuguese	candidate-3.txt	reference-3.txt		0.227803041867
English		candidate-4.txt	reference-4a.txt
							reference-4b.txt
												0.227894952018
