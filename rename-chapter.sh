#!/bin/bash
set -eux
set -o pipefail

OLD_CHAPTER=$1
NEW_NAME=$2

# git mv "$OLD_CHAPTER.asciidoc" "$NEW_NAME.asciidoc"
# mv "$OLD_CHAPTER.html" "$NEW_NAME.html" || touch "$NEW_NAME.html"
#
# if [ -e "tests/test_$OLD_CHAPTER.py" ]; then
#     git mv "tests/test_$OLD_CHAPTER.py" "tests/test_$NEW_NAME.py"
# fi
#
# git mv "source/$OLD_CHAPTER" "source/$NEW_NAME"
#
cd "source/$NEW_NAME/superlists" 
# git checkout "$OLD_CHAPTER"
# git checkout -b "$NEW_NAME"
git checkout "$NEW_NAME"
git push -u local
git push -u origin
cd ../../..

git grep -l "$OLD_CHAPTER" | xargs sed -i '' "s/$OLD_CHAPTER/$NEW_NAME/g"

make "test_$NEW_NAME" || echo -e "\a"

echo git commit -am \'rename "$OLD_CHAPTER" to "$NEW_NAME".\'
