#!/bin/bash
#
# Bash script for producing a nicely LaTeXed file from RST
#


# -- Various Settings -- #

PDFPREFIX="med-"
BASE="/home/med/academic/Public/tex"
PREAMBLE="$BASE/preamble.tex"
RSTCFG="$BASE/rst.conf"
RST=`which rst2latex2`
TEX=`which pdflatex`

# -- End of Settings -- #


TMPCONF=`mktemp`

ASSIGN=`basename ${1} | cut -d'.' -f1`

cp -r "$RSTCFG" "$TMPCONF"
echo "latex-preamble:" >> "$TMPCONF"
sed 's/^/\t/g' "$PREAMBLE" >> "$TMPCONF"
CMD="$RST --conf=$TMPCONF $ASSIGN.rst"
DEST=$ASSIGN.tex
echo $CMD
$CMD > "$DEST"

"$TEX" "$ASSIGN.tex" 
if [ $? -eq 0 ]; then
	echo && echo && echo

	if [ -e "$(ls *.bib)" ]; then
		echo "Processing citations"
		bibtex "$ASSIGN"
		echo && echo && echo
		"$TEX" "$ASSIGN.tex"
	fi

	"$TEX" "$ASSIGN.tex" && mv "$ASSIGN.pdf" "${PDFPREFIX}${ASSIGN}.pdf"

	if [ $? -eq 0 ]; then
                rm -f "$TMPCONF"
		mv *.{log,aux,out} /tmp
		mv *.{blg,bbl} /tmp
		mv "$ASSIGN.tex" /tmp
	fi
else
	return -1
fi

