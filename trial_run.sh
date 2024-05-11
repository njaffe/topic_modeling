#!/bin/bash

# Run create_database.py
python3 utils/create_database.py

# Check if create_database.py ran successfully
if [ $? -eq 0 ]; then
    echo "create_database.py ran successfully, running query_database.py"
    
    # Run query_database.py
    python3 utils/query_database.py "What happens when I block a 4/4 creature with trample and deathtouch with a 1/1 creature?"

    if [ $? -eq 0 ]; then
        echo "query_database.py ran successfully"
    else
        echo "query_database.py encountered an error"
    fi
else
    echo "create_database.py encountered an error"
fi