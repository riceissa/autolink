#!/usr/bin/python3

import argparse
import sys
import datetime
import dateutil.parser
from bs4 import BeautifulSoup
import tld

def main():
    parser = argparse.ArgumentParser(description="autolink v2")
    parser.add_argument("url", type=str, help="the URL")
    parser.add_argument("-f", "--filetype", type=str,
            help="output filetype")
    parser.add_argument("-C", "--citation", action="store_true",
            help="produce citation-style link instead of a hyperlink")
    parser.add_argument("-R", "--reference", action="store_true",
            help="produce a reference-style link for filetypes that support it")
    parser.add_argument("-v", "--verbose", action="store_true",
            help="enable debug messages")
    args = parser.parse_args()
    if args.verbose:
        print("ARGS", args, file=sys.stderr)
    soup = BeautifulSoup(sys.stdin, "html.parser")
    dictionary = soup2dict(soup, url=args.url, verbose=args.verbose)
    if args.verbose:
        print("DICTIONARY", dictionary, file=sys.stderr)
    if args.filetype == "markdown":
        if args.citation:
            out = markdown_citation(dictionary, args.reference)
        else:
            out = markdown_hyperlink(dictionary, args.reference)
    elif args.filetype == "mediawiki":
        if args.citation:
            out = mediawiki_citation(dictionary)
        else:
            out = mediawiki_hyperlink(dictionary)
    elif args.filetype == "html":
        out = html_hyperlink(dictionary)
    else:
        out = plaintext_hyperlink(dictionary)
    print(out, end="")

def sanitize_str(s):
    if isinstance(s, str):
        # Remove nonprinting characters and newlines
        return s.translate(dict.fromkeys(range(32)))
    else:
        print("yikes")
        return ""

def soup2dict(soup, url="", verbose=False):
    """
    Extract info from a BeautifulSoup soup into a dictionary.  Return a new
    dictionary containing metadata fields. They keys that can be in the
    dictionary are "url", "title", "author", "date", "publisher".
    """
    result = dict()
    if url:
        result["url"] = url
    meta = soup.find_all("meta")
    if verbose:
        print(meta, file=sys.stderr)
    for tag in meta:
        if tag.get("property") == "og:title" and tag.get("content"):
            result["title"] = sanitize_str(tag.get("content"))
        elif tag.get("name") == "title":
            result["title"] = sanitize_str(tag.get("content"))
        elif tag.get("name") == "author":
            result["author"] = sanitize_str(tag.get("content"))
        elif tag.get("name") == "article:author_name" and ("author" not in
                result):
            result["author"] = sanitize_str(tag.get("content"))
        elif tag.get("name") == "DCSext.author":
            result["author"] = sanitize_str(tag.get("content"))
        elif tag.get("name") == "dat":
            result["date"] = sanitize_str(tag.get("content"))
        if tag.get("property") == "og:site_name":
            result["publisher"] = sanitize_str(tag.get("content"))
        elif tag.get("name") == "cre":
            result["publisher"] = sanitize_str(tag.get("content"))
        elif tag.get("name") == "dcterms.date":
            result["date"] = sanitize_str(tag.get("content"))
        elif tag.get("property") == "article:published_time":
            result["date"] = sanitize_str(tag.get("content"))
        elif tag.get("property") == "article:modified_time" and ("date" not in
                result):
            result["date"] = (tag.get("content"))
    if "title" not in result and soup.title is not None:
        result["title"] = sanitize_str(soup.title.string)
    if "title" in result:
        result["title"] = sanitize_str(result["title"])
    result = tld_publisher(result, verbose)
    result = convert_date(result, verbose)
    return result

def convert_date(dictionary, verbose=False):
    '''
    Take a dict of metadata.  If a 'date' field exists, return a new dict with
    a standardized date format.  Else return the same dictionary.  In any case,
    do not modify the original dict.
    '''
    if "date" in dictionary:
        date = dateutil.parser.parse(dictionary['date'])
        res = dictionary.copy()
        res['date'] = date.strftime("%B %-d, %Y")
        return res
    else:
        return dictionary

def tld_publisher(dictionary, verbose=False):
    '''
    Take a dict of metadata.  If the top-level domain is in a hard-coded
    dictionary, use that to get the publisher instead of trying to extract it
    from the web page HTML.  Return a new dict that differs at most by the
    'publisher' field without affecting the input dict.
    '''
    try:
        domain = tld.get_tld(dictionary['url'])
    except (tld.exceptions.TldBadUrl, tld.exceptions.TldDomainNotFound):
        if verbose:
            print('Bad TLD; trying with http:// prefix', file=sys.stderr)
        try:
            domain = tld.get_tld('http://' + dictionary['url'])
        except (tld.exceptions.TldBadUrl, tld.exceptions.TldDomainNotFound):
            if verbose:
                print('Still bad TLD; giving up', file=sys.stderr)
            domain = None
    if verbose:
        print('DOMAIN', domain, file=sys.stderr)
    res = dictionary.copy()
    if domain in publisher_map:
        if verbose:
            print('Setting domain because found in publisher_map')
        res['publisher'] = publisher_map[domain]
    return res

def markdown_citation(dictionary, reference_style=False):
    cite_info = ""
    if "author" in dictionary:
        cite_info += dictionary["author"] + ". "
    if "title" in dictionary:
        cite_info += "“" + dictionary["title"] + "”" + ". "
    if "publisher" in dictionary:
        cite_info +=  dictionary["publisher"] + ". "
    if "date" in dictionary:
        date = get_date(dictionary)
        cite_info += date + ". "
    if cite_info:
        cite_info = ' "' + cite_info.strip() + '"'
    if reference_style:
        base = '["{link_text}"][]\n\n[]: {url}{cite_info}'
    else:
        base = '["{link_text}"]({url}{cite_info})'
    link_text = markdown_title(dictionary)
    url = dictionary["url"]
    return base.format(link_text=link_text, url=url, cite_info=cite_info)

def markdown_hyperlink(dictionary, reference_style=False):
    url = dictionary["url"]
    link_text = markdown_title(dictionary)
    if reference_style:
        base = '[{link_text}][]\n\n[]: {url}'
    else:
        base = "[{link_text}]({url})"
    return base.format(link_text=link_text, url=url)

def markdown_title(dictionary):
    # Special characters to backslash-escape from
    # http://pandoc.org/README.html#backslash-escapes . There is also the
    # hyphen, "-", but I've removed that since escaping it just prevents em-
    # and en-dashes from forming (and in most cases, one wants these fancy
    # dashes).
    special_chars = "\\`*_{}[]()>#+.!"
    result = ""
    if "title" in dictionary:
        for c in dictionary["title"]:
            if c in special_chars:
                result += "\\" + c
            else:
                result += c
    return result

def mediawiki_citation(dictionary):
    url = dictionary["url"]
    result = "<ref>{{cite web "
    result += "|url=" + url + " "
    title = ""
    if ("publisher" in dictionary and "title" in dictionary and
            dictionary["title"].endswith(" - " + dictionary["publisher"])):
        title = title[:-len(" - " + publisher)]
    if "author" in dictionary:
        result += "|author=" + dictionary["author"] + " "
    if "date" in dictionary:
        result += "|date=" + dictionary["date"] + " "
    if "title" in dictionary:
        if title:
            result += "|title=" + title + " "
        else:
            result += "|title=" + dictionary["title"] + " "
    if "publisher" in dictionary:
        result += "|publisher=[[" + dictionary["publisher"] + "]] "
    result += "|accessdate=" + datetime.date.today().strftime("%B %-d, %Y")
    result = result.strip()
    result += "}}</ref>"
    return result

def mediawiki_hyperlink(dictionary):
    url = dictionary["url"]
    if "title" in dictionary:
        link_text = dictionary["title"]
        return "[{url} {link_text}]".format(url=url, link_text=link_text)
    else:
        return url

def html_citation(dictionary):
    pass

def html_hyperlink(dictionary):
    if "title" in dictionary:
        link_text = dictionary["title"]
    else:
        link_text = dictionary["url"]
    return '<a href="{}">{}</a>'.format(dictionary["url"], link_text)

def plaintext_citation(dictionary):
    pass

def plaintext_hyperlink(dictionary):
    if "title" in dictionary:
        return "{}: {}".format(dictionary["title"], dictionary["url"])
    else:
        return dictionary["url"]

def get_date(dictionary):
    if "date" in dictionary:
        return dictionary["date"]

publisher_map = {
        "arstechnica.com": "Ars Technica",
        "bloomberg.com": "Businessweek",
        "bostonglobe.com": "The Boston Globe",
        "econlog.econlib.org": "EconLog",
        "economist.com": "The Economist",
        "ft.com": "Financial Times",
        "givewell.org": "GiveWell",
        "huffingtonpost.ca": "Huffington Post Canada",
        "huffingtonpost.com": "The Huffington Post",
        "independent.co.uk": "The Independent",
        "indiatimes.com": "The Times of India",
        "latimes.com": "Los Angeles Times",
        "lesswrong.com": "LessWrong",
        "mirror.co.uk": "Mirror",
        "nybooks.com": "The New York Review of Books",
        "nytimes.com": "The New York Times",
        "plos.org": "PLOS",
        "press.princeton.edu": "Princeton University Press",
        "princeton.edu": "Princeton University",
        "quora.com": "Quora",
        "telegraph.co.uk": "The Telegraph",
        "theatlantic.com": "The Atlantic",
        "theguardian.com": "The Guardian",
        "theregister.co.uk": "The Register",
        "usatoday.com": "USA Today",
        "usnews.com": "U.S. News & World Report",
        "washingtonpost.com": "The Washington Post",
        "who.int": "World Health Organization",
        "wsj.com": "The Wall Street Journal",
}

if __name__ == "__main__":
    main()
