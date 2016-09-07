# autolink
automatically detect the title of a link

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

## Contributing

All contributions are to use the same license as in the LICENSE file.
