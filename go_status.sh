#!/bin/bash
BASE="/home/med/scripts"
MULTIPLEX="${BASE}/dmplex"
FIFO="/tmp/med-status"
EXENAME="statusbar.py"
STATUS="python3 ${BASE}/${EXENAME}"
LOG="status.log"
FONT="cure"

if [ ! -e "${FIFO}" ]; then
	mkfifo "${FIFO}";
fi

RUNNING_TAIL=`ps aux | grep -i ${FIFO} | grep -v grep`
if [ ! -n "${RUNNING_TAIL}"  ]; then
	tail -f "${FIFO}" | "${MULTIPLEX}" | dzen2 -fn ${FONT} -h 11 -ta r -x 200 -p &
fi

PID=`ps aux | grep -i ${EXENAME} | grep -v grep | gawk '{print $2}'`
if [ -n "${PID}" ]; then
	kill ${PID}
fi
exec $STATUS 2>"${BASE}/${LOG}" 
