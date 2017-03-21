# papacy_scraper

A scrapy crawler for papal text archive at vatican.va

___

### Script topic_co_occurrence.py

```
usage: topic_co_occurrence.py [-h] [--input COMPOSITION_SOURCE_FILE]
                              [--output_folder OUTPUT_FOLDER]
                              [--co_occurrence_threshold CO_OCCURRENCE_THRESHOLD]
                              [--reduce_threshold REDUCE_THRESHOLD]
                              [--reduce_write_threshold REDUCE_WRITE_THRESHOLD]

optional arguments:
  -h, --help            show this help message and exit
  --input COMPOSITION_SOURCE_FILE, -i COMPOSITION_SOURCE_FILE
                        Full path and name to source file (MALLET composition file)
  --output_folder OUTPUT_FOLDER, -o OUTPUT_FOLDER
                        Destination folder for output files
  --co_occurrence_threshold CO_OCCURRENCE_THRESHOLD, -c CO_OCCURRENCE_THRESHOLD
                        Reduce to documents: weights below threshold are
                        treated as 0.0 in computation
  --reduce_threshold REDUCE_THRESHOLD, -r REDUCE_THRESHOLD
                        Reduce to documents: reduced weights below threshold
                        are written to output file
  --reduce_write_threshold REDUCE_WRITE_THRESHOLD, -w REDUCE_WRITE_THRESHOLD
                        Threshold for co-occurrence computation - all weights
                        below threshold treated as 0.0
```
example:

```
python topic_co_occurrence.py -i /tmp/tutorial_composition.txt -o /tmp -r 0.01

Computing using argument:
  input:                   C:\tmp\tutorial_composition.txt
  output_folder:           /tmp
  co_occurrence_threshold: 0.15
  reduce_threshold:        0.01
  reduce_write_threshold:  0.0
Output will be stored in:
  co_occurrence_matrix_file: output_co_occurrence_matrix_20170321_142407.csv
  gephi_file: output_gephi_20170321_142407.csv
  reduced_file: output_document_topics_20170321_142407.csv
```


# Failed files

* benedict-xvi_en_angelus_2009_hf-ben-xvi-ang-20090927-brno.txt
* benedict-xvi_en_homilies_2010_hf-ben-xvi-hom-20100606-instr-laboris.txt
* benedict-xvi_en_speeches_2007_february__hf-ben-xvi-spe-20070217-seminario-romano.txt
* benedict-xvi_en_speeches_2010_june__hf-ben-xvi-spe-20100606-catt-maronita.txt
* francesco_en_speeches_2016_april__papa-francesco-20160416-lesvos-cittadinanza.txt