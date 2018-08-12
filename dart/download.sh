#! /bin/bash

URL=http://dart.fss.or.kr/api/xbrl/download/2015_4Q_BS_20160531132458.zip
# wget $URL
FILE_NAME=`echo $URL | sed 's/.*\///g'`
SAVE_DIR=`echo $FILE_NAME | sed 's/_[0-9]*\.zip//g'`
unzip -O euc-kr $FILE_NAME -d $SAVE_DIR
cd $SAVE_DIR
for f in `ls`
do
    iconv -f euc-kr -t utf-8 $f >> $f
done
cd ..

