BASE="/home/med/class/grad/tex"
PREAMBLE="$BASE/preamble.tex"
RSTCFG="$BASE/rst.conf"
RST="/usr/bin/rst2latex.py"

TMPCONF=`mktemp`

ASSIGN=`basename ${1} | cut -d'.' -f1`

cp -r "$RSTCFG" "$TMPCONF"
echo "latex-preamble:" >> "$TMPCONF"
sed 's/^/\t/g' "$PREAMBLE" >> "$TMPCONF"
CMD="python2 $RST --conf=\"$TMPCONF\" \"$ASSIGN.rst\" > \"$ASSIGN.tex\""
echo $CMD
python2 "$RST" --conf="$TMPCONF" "$ASSIGN.rst" > "$ASSIGN.tex"
pdflatex "$ASSIGN.tex" && pdflatex "$ASSIGN.tex" && mv "$ASSIGN.pdf" "med-${ASSIGN}.pdf"

if [ $? -eq 0 ]; then
	rm "$TMPCONF"
	rm *.{out,log,aux}
	rm "$ASSIGN.tex"
fi
