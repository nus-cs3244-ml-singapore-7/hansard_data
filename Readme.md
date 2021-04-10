# Singapore Hansard Data

* Parliament records scraped from 2005-01-12 to 2021-03-05 and stored in hansard_full.zip
* Sessions are captured in a JSON file
  * JSON format changes before 2012-09-10, where the entire HTML file is stored in the JSON instead :/
  * From 2012-09-10, JSON file contains the following:
    * Metadata including date of session, start time, session name
    * Attendance List
    * Permission for MPs to be absent
    * Assent to Bills Passed
    * Actual discussion by MPs with appropriate title and rich formatting
* Some example Bills, Motions and Oral Answers included

---

# Cleaning of data

A `format_hansard.py` file is included to extract speeches and standardise the formatting of the JSON files. The formatted JSON files are written into an output folder. By default, all peripheral text is removed (without the need for any flags). Specific flags are introduced for partial Hansard sessions (e.g. Bills, Motions and Oral Answers) as well as more granular settings (with the `-g` flag). 

---

# Annotation of data

A `formatted_to_txt.py` is included to turn the formatted JSON file into text for annotation. 

The Annotated folder consists of a `config.json` file to be used with [ner-annotator](https://pypi.org/project/ner-annotator/). The annotated files are present and labelled with `_annotated.json`. 

The workflow for annotation was done with the following steps:
1) Download JSON file
2) Format JSON file using format_hansard.py: `python format_hansard.py step_1_file.json -f`, which will give you a step_2_formatted.json file
3) Convert to text: `python formatted_to_txt.py step_2_formatted.json`, which will give you a step_3_text.txt file
4) Use ner_annotator: `ner_annotator step_3_text.txt -c config.json -m hansard`
