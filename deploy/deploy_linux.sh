#!/bin/bash
ver=`awk 'NR==1{ print }' version.txt`
cd ..

prepare_VND=false
prepare_pip=false

echo [1] VND
echo [2] Prepare pip requirements
read choice
case "$choice" in
    1)
        prepare_VND=true
        ;;
    2)
        prepare_pip=true
        ;;
    *)
        echo "Invalid input. Please enter '1' or '2'."
        ;;
esac

if [ "$prepare_VND" = true ]; then
    echo "Preparing VND zip"
    project_folder=$(basename $PWD)
    zipname="$project_folder"_linux_"$ver".zip

    echo "Zipping $project_folder version $ver"
    echo "Zip name: $zipname"
    cd ..

    zip -r --filesync $zipname \
    $project_folder \
    --exclude "*/__pycache__/*"

    echo "Zipping finished. Resulting file:"
    echo $PWD/$zipname
fi

if [ "$prepare_pip" = true ]; then
    echo "Preparing pip requirements"
    env/bin/python -m pip download -r requirements.txt -d downloaded_req
fi
