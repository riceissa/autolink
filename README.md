# autolink
automatically detect the title of a link

```bash
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

## Contributing

All contributions are to use the same license as in the LICENSE file.
