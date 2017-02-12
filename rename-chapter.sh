#!/bin/bash
set -e


OLD_CHAPTER=$1
OLD_XREF=$2
NEW_NAME=$3

sed -i s/$OLD_XREF/$NEW_NAME/g *.asciidoc

git mv $OLD_CHAPTER.asciidoc $NEW_NAME.asciidoc
git mv tests/test_$OLD_CHAPTER.py tests/test_$NEW_NAME.py

mkdir source/$NEW_NAME
git mv source/$OLD_CHAPTER/superlists source/$NEW_NAME/superlists
cd source/$NEW_NAME/superlists && git checkout -b $NEW_NAME && cd ../../..

sed -i s/$OLD_CHAPTER/$NEW_NAME/g .travis.yml atlas.json book.asciidoc copy_html_to_site_and_print_toc.py tests/*.py 
cd source && ./push-back.sh $NEW_NAME && cd ..

xvfb-run -a make test_$NEW_NAME || echo -e "\a"

echo git commit -am \"rename $OLD_CHAPTER $NEW_NAME\"

