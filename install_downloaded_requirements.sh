#!/bin/bash

if_to_install_virtualenv() {
    echo "Your python version:"
    python3 --version
    echo "Would you like to create virtual environment with python3 -m venv env [Y/n]?"
    
    read choice
    case "$choice" in
        yes|YES|y|Y|"")
            echo "Installing virtual env: env"
            python3 -m venv env
            ;;
        no|NO|n|N)
            echo "Doing nothing"
            exit 0
            ;;
        *)
            echo "Invalid input. Please enter 'yes' or 'no'."
            ;;
    esac
}

# Check if virtualenv exists
if test -e "env/bin/python"; then
    echo "Virtual environment exists"
else
    echo "Virtual environment does not exist"
    if_to_install_virtualenv
fi

echo "Installing wheels ..."
cd downloaded_req
for file in *.whl; do
    if [ -f "$file" ]; then
        echo "Processing file: $file"
        pushd ..
        env/bin/python -m pip install --retries 0 downloaded_req/$file
        popd
    fi
done