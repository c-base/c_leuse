#!/bin/bash
export DISPLAY=:0.0
export AVG_DEPLOY=1


###xset -dpms

cd /home/c_leuse/c_leuse/eingangsmonitore/scanner
#echo "running " > /tmp/cleusen_libavg
#while true ; do 
	if [ -x /tmp/STOP_c_leuse ] ; then
		exit 0
	fi
	python  /home/c_leuse/c_leuse/eingangsmonitore/scanner/scanner.py;
	#sleep 3 ;
#done
