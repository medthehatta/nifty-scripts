#!/bin/bash
BASE="/home/med/scripts"
MULTIPLEX="${BASE}/dmplex"
FIFO="/tmp/med-status"
EXENAME="statusbar.py"
STATUS="python2 ${BASE}/${EXENAME}"
LOG="status.log"

if [ ! -e "${FIFO}" ]; then
	mkfifo "${FIFO}";
fi

RUNNING_TAIL=`ps aux | grep -i ${FIFO} | grep -v grep`
if [ ! -n "${RUNNING_TAIL}"  ]; then
	tail -f "${FIFO}" | "${MULTIPLEX}" | dzen2 -fn -*-cure-*-*-*-*-*-*-*-*-*-* -h 11 -ta r -x 200 -p &
fi

PID=`ps aux | grep -i ${EXENAME} | grep -v grep | gawk '{print $2}'`
if [ -n "${PID}" ]; then
	kill ${PID}
fi
$STATUS 2>"${BASE}/${LOG}" &
