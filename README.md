# autolink
automatically detect the title of a link

```
$ ./autolink.py --help
usage: autolink.py [-h] [-f FORMAT] [-c] [-v] url

Get the linked title of URLs (similar to Quora and Facebook)

positional arguments:
  url                   the URL

optional arguments:
  -h, --help            show this help message and exit
  -f FORMAT, --format FORMAT
                        output format; accepted values are 'html', 'markdown',
                        'latex', 'mediawiki'
  -c, --clean           clean the title to remove the site name if the title
                        was obtained from an HTML title tag
  -v, --verbose         enable debug messages
```

## Examples

Note that there is actually no new line at the end of outputs even though these
are inserted here to make the output nicer.
Below `$` indicates the shell prompt.

```
$ ./autolink.py -f markdown "http://causeprioritization.org/Digital%20preservation"
[Digital preservation \- Cause Prioritization Wiki](http://causeprioritization.org/Digital%20preservation)
$ ./autolink.py -f markdown "http://causeprioritization.org/Digital%20preservation" --clean
[Digital preservation](http://causeprioritization.org/Digital%20preservation)
$ ./autolink.py -f markdown "http://lesswrong.com/lw/2as/diseased_thinking_dissolving_questions_about/" --clean
[Diseased thinking: dissolving questions about disease](http://lesswrong.com/lw/2as/diseased_thinking_dissolving_questions_about/)
```

## Contributing

All contributions are to use the same license as in the LICENSE file.
