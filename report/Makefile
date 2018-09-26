.PHONY: clean paper

paper: report.tex report.bib
	pdflatex -enable-write18 report.tex
	bibtex report
	pdflatex -enable-write18 report.tex
	pdflatex -enable-write18 report.tex

clean:
	rm -f report.aux
	rm -f report.toc
	rm -f report.blg
	rm -f report.log
	rm -f report.bbl
	rm -f report.synctex.gz
	rm -f report.out
	rm -f report.spl
	rm -f report.vtc
