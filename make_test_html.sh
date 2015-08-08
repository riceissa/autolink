#!/bin/bash

cd /home/issa/projects/autolink
rm test_html/*.html
python3 generate_test_html.py
rsync --delete -r test_html/ carbon:/var/www/files/public_html/autolink
