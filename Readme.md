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

A `format_hansard.py` file is included to extract speeches and standardise the formatting of the JSON files. The formatted JSON files are written into an output folder. This works for full hansard sessions (with the `-s` flag) and for Bills, Motions and Oral Answers. 

A `formatted_to_txt.py` is also included to turn the formatted JSON file into text for annotation. 

---

The Annotated folder consists of a `config.json` file to be used with [ner-annotator](https://pypi.org/project/ner-annotator/). The annotated files are present and labelled with `_annotated.json`. 