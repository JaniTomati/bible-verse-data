# Bible Verse Data 

This dataset splits the content of the bible into its individual verses[^1]. The bible source text is downloaded from [Project Gutenberg](https://www.gutenberg.org/ebooks/8300)[^2]. 

This repository contains the dataset `bible_verses.csv` and the source code `tokenize_bible.py` used to produce it. 

Alternatively, the option to split the text into its individual sentences is given in the source code, however, there may be more preprocessing necessary to produce sufficient results. 

## Data domain 

* testament_title := title of the testament [old_testament, new_testament]
* book_id := unique book identifier 
* verse_id := unique verse dentifier
* bible_verse := unique verse identifier per book 
* text := full text of a verse
* #chars := number of characters in a verse
* #words := number of words in a verse
* lexical_richness := Type-Token Ratio of a verse
* lexical_novelty := [Lexical Novelty](https://datamining.typepad.com/data_mining/2011/09/visualizing-lexical-novelty-in-literature.html)[^3] of a verse in a book

[^1]: Sentences that are not part of a verse are not included in the dataset.
[^2]: Challoner's revised Douay-Rheims Version (Old Testament 1609 & 1610, New Testament 1582). The Whole Revised and Diligently Compared with the Latin Vulgate by Bishop Richard Challoner A.D. 1749-1752, EBook-No. 8300.
[^3]: Hurst, M. (2011). Visualizing Lexical Novelty in Literature. URL [https://datamining.typepad.com/data_mining/2011/09/visualizing-lexical-novelty-in-literature.html](https://datamining.typepad.com/data_mining/2011/09/visualizing-lexical-novelty-in-literature.html).
