#!/bin/sh
i=0
while [ $i -ne 30 ]
do
        i=$(($i+1))
        rotatedir="/archives/rotate$i";
	if [ ! -d "/archives/rotate$i" ]
	then
	   mkdir "/archives/rotate$i"
	   echo $rotatedir;
        fi
done

rm -rf /archives/rotate30/*
mv /archives/rotate29/* /archives/rotate30/
mv /archives/rotate28/* /archives/rotate29/
mv /archives/rotate27/* /archives/rotate28/
mv /archives/rotate26/* /archives/rotate27/
mv /archives/rotate25/* /archives/rotate26/
mv /archives/rotate24/* /archives/rotate25/
mv /archives/rotate23/* /archives/rotate24/
mv /archives/rotate22/* /archives/rotate23/
mv /archives/rotate21/* /archives/rotate22/
mv /archives/rotate20/* /archives/rotate21/
mv /archives/rotate19/* /archives/rotate20/
mv /archives/rotate18/* /archives/rotate19/
mv /archives/rotate17/* /archives/rotate18/
mv /archives/rotate16/* /archives/rotate17/
mv /archives/rotate15/* /archives/rotate16/
mv /archives/rotate14/* /archives/rotate15/
mv /archives/rotate13/* /archives/rotate14/
mv /archives/rotate12/* /archives/rotate13/
mv /archives/rotate11/* /archives/rotate12/
mv /archives/rotate10/* /archives/rotate11/
mv /archives/rotate9/* /archives/rotate10/
mv /archives/rotate8/* /archives/rotate9/
mv /archives/rotate7/* /archives/rotate8/
mv /archives/rotate6/* /archives/rotate7/
mv /archives/rotate5/* /archives/rotate6/
mv /archives/rotate4/* /archives/rotate5/
mv /archives/rotate3/* /archives/rotate4/
mv /archives/rotate2/* /archives/rotate3/
mv /archives/rotate1/* /archives/rotate2/

