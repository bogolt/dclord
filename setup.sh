#!/bin/sh

APP="dcLord"
SRC=$APP"/src"
RES=$APP"/res"

if [ ! -d $APP ]
then
	mkdir $APP
fi

if [ ! -d $RES ]
then
	mkdir $RES
fi

if [ ! -d $SRC ]
then
	mkdir $SRC
fi

cp src/*.py dcLord/src/
cp res/*.xrc dcLord/res/
cp ./dcLord.sh dcLord/dcLord.sh

tar cjf dcLord.tar.bz2 dcLord
zip -r dcLord_src.zip dcLord
