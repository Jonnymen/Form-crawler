# Form-crawler
Identify forms on website

```
usage: form_crawler.py [-h] [-d DEPTH] [-v VERBOSE] [--same-domain] [--no-same-domain] [-o OUTPUT] url

Identify forms on a website.

positional arguments:
  url                   the target website URL

options:
  -h, --help            show this help message and exit
  -d DEPTH, --depth DEPTH
                        the maximum depth of recursion, default=1
  -v VERBOSE, --verbose VERBOSE
                        Output verbosity
                        1 - Only found forms
                        2 - All crawled sites
                        3 - Granular logging
  --same-domain         whether to stay on the same domain or not (default)
  --no-same-domain      whether to stay on the same domain or not
  -o OUTPUT, --output OUTPUT
                        Save output to file, provide filename
```
