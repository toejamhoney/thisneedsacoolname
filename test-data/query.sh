#!/bin/bash

while read line
do
        md5=$line
        psql 500k-test -qAt -c "select tree_md5 from parsed_pdfs where pdf_md5='$line'" >> query-$1.out
done < $1
