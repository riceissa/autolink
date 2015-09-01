#!/usr/bin/python3
# -*- coding: utf-8 -*-

import argparse
import io
import logging
import sys
import requests
import urllib3
import tld
from tld import get_tld
from bs4 import BeautifulSoup
import html
from PyPDF2 import PdfFileReader, PdfFileWriter

def main():
    # See https://blog.quora.com/Launched-Customizable-Links for Quora's
    # launch post
    parser = argparse.ArgumentParser(description=("Get the linked title of " +
        "URLs (similar to Quora and Facebook)"))
    parser.add_argument("url", type=str, help="the URL")
    parser.add_argument("-f", "--format", type=str,
            help=("output format; accepted values are 'none', 'html', " +
            "'markdown', 'latex', 'mediawiki'"))
    parser.add_argument("-c", "--clean", action="store_true",
            help=("clean the title to remove the site name " +
            "if the title was obtained from an HTML title tag"))
    parser.add_argument("-v", "--verbose", action="store_const",
        dest="log_level", const=logging.DEBUG, help="enable debug messages")
    args = parser.parse_args()
    logging.basicConfig(level=args.log_level)

    url = args.url
    logging.debug("Trying first attempt")
    attempt_1 = try_url(url, args.format, clean=args.clean)
    if attempt_1["exit"]:
        logging.debug("First attempt succeeded!")
        print(attempt_1["text"], end="")
    else:
        logging.debug("First attempt failed; trying second attempt")
        attempt_2 = try_url("http://" + url, args.format, clean=args.clean)
        if attempt_2["exit"]:
            logging.debug("Second attempt succeeded!")
            print(attempt_2["text"], end="")
        else:
            logging.debug("Second attempted failed; using result " +
                "from first attempt")
            print(attempt_1["text"], end="")

def try_url(url, fmt, clean=False):
    '''
    Return (Str, True) if succeeded; (Str, False) otherwise.
    '''
    result = {}
    analyte = analyze_url(url)
    if analyte:
        return {"text": analyte, "exit": True}
    try:
        user_agent = ("Mozilla/5.0 (X11; Linux i686; rv:31.0) Gecko/20100101 " +
            "Firefox/31.0 Iceweasel/31.5.0")
        headers = {"User-Agent": user_agent}
        response = requests.get(url, stream=True, headers=headers)
        url = response.url
        if  ("text/html" in response.headers["content-type"] or
                "application/pdf" in response.headers["content-type"]):
            logging.debug("HTML page or PDF file detected")
            if "text/html" in response.headers["content-type"]:
                # <title> is probably in the first around 10MB of HTML
                # files, so we can download less here than in the case
                # for PDFs
                logging.debug("HTML detected")
                doc = response.iter_content(chunk_size=1000)
            else:
                # PDFs might require more downloading
                logging.debug("PDF detected")
                doc = response.iter_content(chunk_size=1000000)
            data = next(doc)
            result["text"] = get_filetype_link(
                get_link_text(url, response.headers["content-type"], data=data,
                    clean=clean),
                url,
                fmt
            )
        else:
            logging.debug("No HTML page detected")
            result["text"] = get_filetype_link(
                get_link_text(url, response.headers["content-type"]),
                url,
                fmt
            )
        result["exit"] = True
    except (requests.exceptions.MissingSchema,
            requests.exceptions.ConnectionError,
            requests.exceptions.InvalidSchema,
            urllib3.exceptions.LocationParseError):
        # since it's not a valid URL, just return it
        result["text"] = url
        result["exit"] = False
    return result

def analyze_url(url):
    """
    Look just at the URL to see if a suitable title text can be found.  This
    method is much faster than actually visiting the URL to find the title
    element in the downloaded file. We want to do this for special sites like
    Facebook, which doesn't allow anonymous downloading of certain pages, like
    group pages.

    Args:
        url: A string that is a URL

    Returns:
        A string that is the title text to be used. If no suitable title text
        can be produced, return the empty string, "".
    """
    try:
        tl = get_tld(url)
    except (tld.exceptions.TldBadUrl, tld.exceptions.TldDomainNotFound):
        logging.debug("bad TLD; trying with http:// prefix")
        try:
            tl = get_tld("http://" + url)
        except (tld.exceptions.TldBadUrl, tld.exceptions.TldDomainNotFound):
            logging.debug("still bad TLD; giving up")
            return ""
    if tl == "facebook.com" and "facebook.com/groups/" in url:
            return "Facebook group page post"
    return ""

def get_filetype_link(link_text, url, filetype):
    """
    Put the pieces together and produce a valid hyperlink for given output
    filetype.

    Args:
        link_text: A string representing the displayed or linked text when
            linking to something, e.g. "hello" in <a
            href="http://example.org">hello<a>. This string should already be in
            the intended form; i.e. all HTML escapes should have been unescaped
            at this point.
        url: A string of the URL.
        filetype: A string of the output filetype. Accepted parameters are:
            "none", "html", "markdown", "latex".

    Returns:
        A string that is a valid hyperlink for the specified output filetype.
    """
    if filetype == "markdown":
        # From http://pandoc.org/README.html#backslash-escapes
        special_chars = "\\`*_{}[]()>#+-.!"
        result = ""
        for c in link_text:
            if c in special_chars:
                result += "\\" + c
            else:
                result += c
        return "[{link_text}]({url})".format(link_text=result, url=url)
    if filetype == "html":
        return '<a href="{url}">{link_text}</a>'.format(url=url,
                link_text=html.escape(link_text))
    if filetype == "mediawiki":
        return "[{url} {link_text}]".format(url=url,
                link_text=link_text)
    if filetype == "latex":
        # LaTeX is really sensitive about special characters so this
        # probably needs a lot of tweaking
        special_chars = "$&%{_#"
        result = ""
        for c in link_text:
            if c in special_chars:
                result += "\\" + c
            elif c == "\\":
                result += "\\textbackslash{}"
            elif c == "~":
                result += "\\textasciitilde{}"
            else:
                result += c
        clean_url = ""
        for c in url:
            if c in special_chars or c in "~":
                clean_url += "\\" + c
            elif c == "\\":
                clean_url += "{\\textbackslash}"
            else:
                clean_url += c
        return ("\\href{%s}{%s}" % (clean_url, result))
    else:
        return "{link_text}: {url}".format(url=url, link_text=link_text)

def get_link_text(url, mime_type, data=None, clean=False):
    '''
    Take URL, MIME type, and optional data to produce the link text.
    '''
    tld = get_tld(url)
    result = "File on " + tld
    if mime_type.startswith("image"):
        result = "Image on " + tld
    elif  "application/pdf" in mime_type:
        logging.debug("PDF detected")
        # I need seek() for some reason so convert from bytes
        data = io.BytesIO(data)
        # fix this later, but I always get a "PdfReadWarning: Xref table
        # not zero-indexed" which should only happen when the -v flag is
        # present
        import warnings
        warnings.filterwarnings("ignore")
        pdf = PdfFileReader(data, strict=True)
        # PyPDF2 somehow thinks many PDFs are encrypted with the empty
        # string, so deal with that
        if pdf.isEncrypted:
            pdf.decrypt('')
        result = pdf.getDocumentInfo().title
        #result = "PDF on " + tld
    elif "text/html" in mime_type:
        try:
            soup = BeautifulSoup(data, 'html.parser')
            meta = soup.find_all("meta")
            og_title_lst = []
            twitter_title_lst = []
            meta_title_lst = []
            schema_lst = []
            for i in meta:
                if i.get("property") == "og:title":
                    og_title_lst.append(i.get("content"))
                elif i.get("property") == "twitter:title":
                    twitter_title_lst.append(i.get("content"))
                elif i.get("name") == "title":
                    meta_title_lst.append(i.get("content"))
                elif i.get("itemprop") == "name":
                    schema_lst.append(i.get("content"))
            if og_title_lst:
                logging.debug("found og:title")
                result = og_title_lst[0].strip()
            elif twitter_title_lst:
                logging.debug("found twitter title")
                result = twitter_title_lst[0].strip()
            elif meta_title_lst:
                logging.debug("found meta name title")
                result = meta_title_lst[0].strip()
            elif schema_lst:
                logging.debug("found schema title")
                result = schema_lst[0].strip()
            elif soup.title and soup.title.string:
                logging.debug("found title tag")
                result = html.unescape(soup.title.string)
                if clean:
                    result = messy_title_parse(result)
            else:
                logging.debug("no title found; using default")
                result = "Page on " + tld
        except AttributeError:
            # Probably just empty title when trying to get
            # soup.title.string
            logging.debug("FIXME: this isn't supposed to happen")
            result = "Page on " + tld
    if len(result) > 255:
        result = result[:253] + " …"

    return result

def messy_title_parse(title, url=None):
    # Even if nothing works, at least we'll have a whitespace-sanitized
    # title
    logging.debug("Cleaning messy title")
    result = title.strip()
    hyphen_split = result.split(" - ")
    bar_split = result.split(" | ")
    em_dash_split = result.split(" — ")
    colon_split = result.split(": ")
    if len(hyphen_split) > 1:
        # So there is actually more than one part, so we just take the
        # first and we're done.  This is for titles like "Post Title -
        # Site Name"
        result = hyphen_split[0]
    elif len(em_dash_split) > 1:
        result = em_dash_split[0]
    elif len(bar_split) > 1:
        result = bar_split[0]
    elif len(colon_split) > 1:
        # For titles like "Site Name: Post Title"
        result = colon_split[-1]
    return result

if __name__ == "__main__":
    main()
