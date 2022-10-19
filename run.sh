#!/bin/bash

printf "python3 make_database.py\n"
python3 make_database.py
printf "python3 error_messages\n"
python3 error_messages.py
for f in *.messages; do echo $f; perl parse_messages.pl $f; echo; done > messages.summary
printf "Data processing complete! Now run the analysis scripts at your leisure.\n"

