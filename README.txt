USAGE:
=====
	For any script you can get more details options with:
	$python3 <script.py> -h



*******************
   import.py 
*******************
	
	Resume:
	------
	This script is dedicated to import full text from solr by platform (required option), by selected years and by langage.
	Each text is saved in one file. The file is saved under a directory of its year.

 
	settings :
	---------
		You need first to specify your solr url in the settings.py

	Exemple:
	-------
		To import french text for revues.org published in 2005 and 2007:  
		$python3 import.py -p RO -i 2005 2007 -l fr -d mydirectory
	
	Note:
	----
		The -q --query option is not yet implemented. ['fr', 'en', 'es'..]: OpenEdition abbreviation for specified a langage.


******************
   topics.py
******************
	Resume:
	------
	This script is dedicated to:
		-Get a corpus directory.
		-Clean and/or stem each documents of this corpus and fit this corpus for gensim format.
		-Bag of word model
		-TfIdf transformation.
		-LDA Model (in multiprocess) is running (according to seyting option) to:
			-Fit alpha parameter and number of topics. A csv file is generated to evaluate the log_perplexity.
			-Generate a Topic Model


	Files generated:
	--------------
		GENSIM FORMAT TEXT: '/tmp/gensim_docs.txt' is generated. A big file.txt  where one line is on document. (format required for gensim) 
		LOG: './lda_model.log' (by default) is always saved on the current directory (logging python library)
		FIT PARAMETERS: (when option -f=True): './fit_result.csv' is saved on a current directory. This file could be used for visualisation in graph.py
		TRAIN MODEL: (option -f=False; default option):  './lda.model.expElogbeta.npy', './lda.model.id2word', './lda.model.state', './lda.model' is saved on current directory. ONLY 'lda.model' could be used for data visualisation in topic_visualisation.py

	dictionary:
	---------
		By default a stop_tartarus.txt (http://snowball.tartarus.org/algorithms/french/stemmer.html) anda stop_calenda.txt is furnished. This a list of stop word

	Exemple:
	-------
		To fit the best parameter with gensim info log for french text (documents is under directory train):  
		$./topics.py -l french -d train -f True -vvv
		To train the model on a french corpus:
		$./topics -l english -d train

	
	Note:
	----
		Take care of memory overloading in python multiprocessing. See option -m for details. ['french', 'english', 'spanish'..]: stemmer abbreviation for specified a langage.


*******************
   graph.py 
*******************
Resume:
------
This script is dedicated to plot 2 file.pdf to appreciate the right alpha parameter and the right number of topics for the corpus. 

	Required:
	--------
 		'./fit_result.csv' file must be present in the current dirctory to run graph.py. See above (topics.py)to know how to generate it.

	Files generated:
	--------------
		Num_topics_correlation.pdf and Alpha_correlation.pdf in the current directory.
		To have a better idea of log_perplexity (http://psiexp.ss.uci.edu/research/papers/sciencetopics.pdf)  



*******************
   topics_visu.py 
*******************
Resume:
------
In order to appreciate This script is dedicated to plot 2 file.pdf to appreciate the right alpha parameter and the right number of topics for the corpus. 

	Required:
	--------
 		'./lda.model' file must be present in the current dirctory to run topics_visu.py. See above (topics.py)to know how to generate it.

	Files generated:
	--------------
		'./output_file.txt' . This file is text file which represente a flat list of word per topics
		i file :'./WordCloud{i}.pdf' where i is the number of topics. It represents a word cloud of each topic. Size of word is proportional of probability of the word in the topic.

	Notes:
	-----
		Be careful you generate as many pdf files as number of topics


*******************
   Full pipeline
*******************
Resume:
-----
	A full pipeline could be:
		- import a specific data for a specific platform and a specific langage: (import.py)
		- Fit parameters (long, long running time) with option -f: (topics.py)
		- Analysed result to select the best parameters: (graph.py)
		- Training model (long running time) with choosen parameters above (topics.py)
		- Vizualised and analysed topics and words by topics (topics_visu.py)


