#!/bin/bash
set -euo pipefail
IFS=$'\n\t'

# generate sample data
echo "Demo times:"
time python3 -X importtime demo.py 2> imports.log

echo -e "\nSample data has been created! Take a look at the Demo times, that are the times that took to run the demo.py script."
echo -e "Now it's time to see it live!\n"
echo "You have to run the following commands:"
echo "$ cd ../"
echo -e "$ python3 app.py\n"
echo "Then, simply open your broswer at http://127.0.0.1:5000 and uplodd the imports.log that we created!" 
