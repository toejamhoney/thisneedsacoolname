#! /bin/bash

#psql -h 10.9.8.100 -d 500k-test -c "SELECT pdf_md5 FROM parsed_pdfs WHERE obf_js LIKE '%.syncAnnotScan%' and length(de_js) <1;" | while read pdf_md5
psql -h 10.9.8.100 -d 500k-test -t -c "SELECT pdf_md5 FROM parsed_pdfs WHERE tree_md5='732d6592ba3bec74575713ba78b8dacf' LIMIT 10;" | while read pdf_md5
do
#echo '*' $pdf_md5
    js=`psql -h 10.9.8.100 -d 500k-test -t -c "SELECT obf_js FROM parsed_pdfs WHERE pdf_md5='"$pdf_md5"';"`
    tree=`psql -h 10.9.8.100 -d 500k-test -t -c "SELECT tree FROM parsed_pdfs WHERE pdf_md5='"$pdf_md5"';"`
        js=`echo $js | sed 's/\\\r \+//g' | sed 's/ \+ //g' | sed 's/split(\/\-\/)/split([^0-9a-f])/g'`
        tree=`echo $tree | sed 's/\\\r \+//g' | sed 's/ \+ //g'`
#echo '***\n'$tree
python -c "__import__('JSAnalysis').analyse('"$obf_js"', __import__('lxml.etree').etree.fromstring(\"\"\"$tree\"\"\"))"
#echo "__import__('JSAnalysis').analyse('"$obf_js"', __import__('lxml.etree').etree.fromstring('"$tree"'))"
#echo '***\r' $obf_js
done