# autolink
automatically detect the title of a link

**NOTE: I no longer use this script, and it is not maintained. Instead, I use
[citewebgen](https://github.com/riceissa/citewebgen),
which is a JavaScript version of this that works directly from the browser,
and works as a bookmarklet.**

    usage: autolink.py [-h] [-f FILETYPE] [-C] [-R] [-v] url

    autolink v2

    positional arguments:
      url                   the URL

    optional arguments:
      -h, --help            show this help message and exit
      -f FILETYPE, --filetype FILETYPE
                            output filetype
      -C, --citation        produce citation-style link instead of a hyperlink
      -R, --reference       produce a reference-style link for filetypes that
                            support it
      -v, --verbose         enable debug messages

## Examples

Below `%` indicates the shell prompt.

    % URL='http://googlewebmastercentral.blogspot.com/2013/04/5-common-mistakes-with-relcanonical.html' ; curl --silent --compressed -L "$URL" | ./autolink.py -f markdown -C "$URL"
    ["5 common mistakes with rel=canonical"](http://googlewebmastercentral.blogspot.com/2013/04/5-common-mistakes-with-relcanonical.html "“5 common mistakes with rel=canonical”. Official Google Webmaster Central Blog.")
    % URL='http://predictionbook.com/predictions/8161'
    % curl --silent --compressed -L $URL | \
        ./autolink.py -f mediawiki -C $URL
    <ref>{{cite web |url=http://predictionbook.com/predictions/8161 |title=PredictionBook: LSD: I will experience any kind of 'flashback' within 5 years. |accessdate=September 7, 2016}}</ref>

## Contributing

All contributions are to use the same license as in the LICENSE file.
