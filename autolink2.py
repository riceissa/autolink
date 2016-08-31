#!/usr/bin/python3

import argparse
import sys
import datetime
from bs4 import BeautifulSoup

def main():
    parser = argparse.ArgumentParser(description="autolink v2")
    parser.add_argument("url", type=str, help="the URL")
    parser.add_argument("-f", "--filetype", type=str,
            help="output filetype")
    args = parser.parse_args()

    soup = BeautifulSoup(sys.stdin, "html.parser")
    dictionary = soup2dict(soup, args.url)
    print(dictionary)
    if args.filetype == "markdown":
        out = markdown_hyperlink(dictionary)
    elif args.filetype == "mediawiki":
        out = mediawiki_citation(dictionary)
    else:
        out = plaintext_hyperlink(dictionary)
    print(out, end="")

def soup2dict(soup, url=""):
    """
    Extract info from a BeautifulSoup soup into a dictionary.  Return a new
    dictionary containing metadata fields. They keys that can be in the
    dictionary are "url", "title", "author", "date", "publisher".
    """
    result = dict()
    if url:
        result["url"] = url
    meta = soup.find_all("meta")
    print(meta)
    for tag in meta:
        if tag.get("property") == "og:title" and tag.get("content"):
            result["title"] = tag.get("content")
        elif tag.get("name") == "title":
            result["title"] = tag.get("content")
        elif tag.get("name") == "author":
            result["author"] = tag.get("content")
        elif tag.get("name") == "article:author_name" and ("author" not in
                result):
            result["author"] = tag.get("content")
        elif tag.get("name") == "DCSext.author":
            result["author"] = tag.get("content")
        elif tag.get("name") == "dat":
            result["date"] = tag.get("content")
        if tag.get("property") == "og:site_name":
            result["publisher"] = tag.get("content")
        elif tag.get("name") == "cre":
            result["publisher"] = tag.get("content")
        elif tag.get("name") == "dcterms.date":
            result["date"] = tag.get("content")
        elif tag.get("property") == "article:published_time":
            result["date"] = tag.get("content")
        elif tag.get("property") == "article:modified_time" and ("date" not in
                result):
            result["date"] = tag.get("content")
    if "title" not in result and soup.title is not None:
        result["title"] = soup.title.string
    if "title" in result:
        # Remove nonprinting characters and newlines
        result["title"] = result["title"].translate(dict.fromkeys(range(32)))
    return result

def markdown_citation(dictionary, reference_style=False):
    pass

def markdown_hyperlink(dictionary, reference_style=False):
    # From http://pandoc.org/README.html#backslash-escapes
    # There is also the hyphen, "-", but I've removed that since
    # escaping it just prevents em- and en-dashes from forming (and
    # in most cases, this is what one wants)
    special_chars = "\\`*_{}[]()>#+.!"
    result = ""
    url = dictionary["url"]
    link_text = dictionary["title"]
    for c in link_text:
        if c in special_chars:
            result += "\\" + c
        else:
            result += c
    return "[{link_text}]({url})".format(link_text=result, url=url)

def mediawiki_citation(dictionary):
    pass

def mediawiki_hyperlink(dictionary):
    pass

def plaintext_citation(dictionary):
    pass

def plaintext_hyperlink(dictionary):
    if "title" in dictionary:
        return "{}: {}".format(dictionary["title"], dictionary["url"])
    else:
        return dictionary["url"]

if __name__ == "__main__":
    main()
