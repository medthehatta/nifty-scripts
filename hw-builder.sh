BASE="/home/med/class/grad/tex"
PREAMBLE="$BASE/preamble.tex"
RSTCFG="$BASE/rst.conf"
RST="/usr/bin/rst2latex.py"

TMPCONF=`mktemp`

ASSIGN=`basename ${1} | cut -d'.' -f1`

cp -r "$RSTCFG" "$TMPCONF"
echo "latex-preamble:" >> "$TMPCONF"
sed 's/^/\t/g' "$PREAMBLE" >> "$TMPCONF"
CMD="python2 $RST --conf=$TMPCONF $ASSIGN.rst"
DEST=$ASSIGN.tex
echo $CMD
$CMD > "$DEST"

pdflatex "$ASSIGN.tex" 
if [ $? -eq 0 ]; then
	echo && echo && echo

	if [ -e "$ASSIGN.sage" ]; then
		echo "$ASSIGN.sage Found in $(pwd)."
		sage "$ASSIGN.sage"
	fi

	if [ -n $(ls *.bib) ]; then
		echo "Bibfile found in $(pwd)."
		bibtex "$ASSIGN"
		echo && echo && echo
		pdflatex "$ASSIGN.tex"
	fi

	pdflatex "$ASSIGN.tex" && mv "$ASSIGN.pdf" "med-${ASSIGN}.pdf"

	if [ $? -eq 0 ]; then
		rm -f "$TMPCONF"
		rm -f *.{out,log,aux}
		rm -f *.{blg,bbl}
		#rm -f "$ASSIGN".{sage,py,sout}
		rm -rf sage-plots-for*
		rm -f "$ASSIGN.tex"
	fi
fi

