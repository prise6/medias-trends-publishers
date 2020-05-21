#!/bin/sh

PROJECT_DIR=`pwd`
WEBSITE_DIR=website
WEBSITE_INDEX_PATH=$WEBSITE_DIR/index.html
WEBSITE_BRANCH=website
ORIGIN_REPO=github-ssh
PYTHON=python3
DATE_NOW=`date +%Y%m%d%H%M`
WEBSITE_CHANGED=0

echo "PROJECT_DIR:        $PROJECT_DIR"
echo "WEBSITE_DIR:        $WEBSITE_DIR"
echo "WEBSITE_INDEX_PATH: $WEBSITE_INDEX_PATH"
echo "WEBSITE_BRANCH:     $WEBSITE_BRANCH"
echo "ORIGIN_REPO:        $ORIGIN_REPO"
echo "DATE_NOW:           $DATE_NOW"

git checkout $WEBSITE_BRANCH
git pull --rebase $ORIGIN_REPO master

$PYTHON -m mtpublishers.cli publish -p website

git diff --name-only --exit-code | grep -q $WEBSITE_INDEX_PATH

if [ $? -eq 0 ]; then
    echo "Info: Website is updated"
    git add $WEBSITE_INDEX_PATH
    git commit -m"Website: update $DATE_NOW"
    echo "Info: Deploying website..."
    git push $ORIGIN_REPO $WEBSITE_BRANCH
else 
    echo "Info: Website is not updated"
fi

echo "Info: Done."