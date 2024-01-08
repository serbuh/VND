#!/bin/bash
ver=`awk 'NR==1{ print }' version.txt`
cd ..

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