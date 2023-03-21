#!/usr/bin/env python3

import sys
import os
import requests
from bs4 import BeautifulSoup
import argparse
import datetime
import logging
from urllib.parse import urlparse

def setupLogger(verbosity=logging.CRITICAL, out_file=""):

    class DebugFilter(logging.Filter):
        def filter(self, record):
            return record.levelno == logging.DEBUG

    class InfoFilter(logging.Filter):
        def filter(self, record):
            return record.levelno == logging.INFO

    class WarningFilter(logging.Filter):
        def filter(self, record):
            return record.levelno == logging.WARNING

    class ErrorFilter(logging.Filter):
        def filter(self, record):
            return record.levelno == logging.ERROR

    class CriticalFilter(logging.Filter):
        def filter(self, record):
            return record.levelno == logging.CRITICAL

    logger = logging.getLogger("form_crawler")
    logger.setLevel(verbosity)

    formatter_critical = logging.Formatter("\033[32m" + "[+] %(message)s" + "\033[0m")
    formatter_error = logging.Formatter("\033[31m" + "[-] %(message)s" + "\033[0m")
    formatter_warning = logging.Formatter("\033[33m" + "[?] %(message)s" + "\033[0m")
    formatter_info = logging.Formatter("[i] %(message)s")
    formatter_debug = logging.Formatter("[d] %(message)s")

    handler_critical = logging.StreamHandler()
    handler_critical.setLevel(logging.CRITICAL)
    handler_critical.addFilter(CriticalFilter())
    handler_critical.setFormatter(formatter_critical)

    handler_error = logging.StreamHandler()
    handler_error.setLevel(logging.ERROR)
    handler_error.addFilter(ErrorFilter())
    handler_error.setFormatter(formatter_error)

    handler_warning = logging.StreamHandler()
    handler_warning.setLevel(logging.WARNING)
    handler_warning.addFilter(WarningFilter())
    handler_warning.setFormatter(formatter_warning)

    handler_info = logging.StreamHandler()
    handler_info.setLevel(logging.INFO)
    handler_info.addFilter(InfoFilter())
    handler_info.setFormatter(formatter_info)

    handler_debug = logging.StreamHandler()
    handler_debug.setLevel(logging.DEBUG)
    handler_debug.addFilter(DebugFilter())
    handler_debug.setFormatter(formatter_debug)

    if out_file != "":
        formatter_critical_f = logging.Formatter("[+] %(message)s")
        formatter_error_f = logging.Formatter("[-] %(message)s")
        formatter_warning_f = logging.Formatter("[?] %(message)s")
        formatter_info_f = logging.Formatter("[i] %(message)s")
        formatter_debug_f = logging.Formatter("[d] %(message)s")
        
        handler_critical_f = logging.FileHandler(out_file)
        handler_critical_f.setLevel(logging.CRITICAL)
        handler_critical_f.addFilter(CriticalFilter())
        handler_critical_f.setFormatter(formatter_critical_f)

        handler_error_f = logging.FileHandler(out_file)
        handler_error_f.setLevel(logging.ERROR)
        handler_error_f.addFilter(ErrorFilter())
        handler_error_f.setFormatter(formatter_error_f)

        handler_warning_f = logging.FileHandler(out_file)
        handler_warning_f.setLevel(logging.WARNING)
        handler_warning_f.addFilter(WarningFilter())
        handler_warning_f.setFormatter(formatter_warning_f)

        handler_info_f = logging.FileHandler(out_file)
        handler_info_f.setLevel(logging.INFO)
        handler_info_f.addFilter(InfoFilter())
        handler_info_f.setFormatter(formatter_info_f)

        handler_debug_f = logging.FileHandler(out_file)
        handler_debug_f.setLevel(logging.DEBUG)
        handler_debug_f.addFilter(DebugFilter())
        handler_debug_f.setFormatter(formatter_debug_f)

        logger.addHandler(handler_critical_f)
        logger.addHandler(handler_error_f)
        logger.addHandler(handler_warning_f)
        logger.addHandler(handler_info_f)
        logger.addHandler(handler_debug_f)

    logger.addHandler(handler_critical)
    logger.addHandler(handler_error)
    logger.addHandler(handler_warning)
    logger.addHandler(handler_info)
    logger.addHandler(handler_debug)

def print_banner(url, depth, vmsg, verbosity, same_domain=True, out_file=""):

    current_datetime = datetime.datetime.now()
    formatted_datetime = current_datetime.strftime('%a %b %d %H:%M:%S %Y')

    if out_file == "":
        out = False
        out_file = "[not specified]"
    else:
        out = True

    banner = f'''
=============================
Form_crawler v1.0
by Jan Mensik
=============================

{formatted_datetime}

Starting url:   {url}
Crawl depth:    {depth}
Verbosity:      {verbosity} ({vmsg})
Stay on domain: {same_domain}
Output file:    {out_file}

=============================
'''

    print(banner)

    if out:
        with open(out_file, 'w') as file:
            file.write(banner + "\n")


def find_forms(url, depth, same_domain=True):
    try:
        logger = logging.getLogger("form_crawler")
        logger.warning("Crawling site: " + url)
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')
        forms = soup.find_all('form')
        if len(forms) != 0:
            for form in forms:
                form_name = form.get('name', '[no name specified]')
                logger.critical(f"{url} - \"{form_name}\"")
        else:
            logger.error("Nothing found ...")

        if depth != 0:
            for link in soup.find_all('a'):
                href = link.get('href')
                if href.startswith('/'):
                    href = urlparse(url).scheme + '://' + urlparse(url).netloc + href
                logger.info("Found hyperlink: " + href)
                if same_domain and urlparse(href).netloc != urlparse(url).netloc:
                    logger.info("Not same domain, skipping ...")
                    continue
                if href.startswith(url):
                    find_forms(href, depth - 1, same_domain)
    except Exception as e:
        print(f"Error: {e}")

def positive_int(value):
    ivalue = int(value)
    if ivalue < 1:
        raise argparse.ArgumentTypeError("%s is not valid positive integer!" % value)
    return ivalue

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Identify forms on a website.', formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('url', type=str, help='the target website URL')
    parser.add_argument('-d','--depth', type=positive_int, default=1, help='the maximum depth of recursion, default=1')
    parser.add_argument('-v', '--verbose', type=int, default=1, help='Output verbosity\n1 - Only found forms\n2 - All crawled sites\n3 - Granular logging')
    parser.add_argument('--same-domain', dest='same_domain', action='store_true', help='whether to stay on the same domain or not (default)')
    parser.add_argument('--no-same-domain', dest='same_domain', action='store_false', help='whether to stay on the same domain or not')
    parser.add_argument('-o','--output', type=str, default='', help='Save output to file, provide filename')
    parser.set_defaults(same_domain=True)
    args = parser.parse_args()
    
    if args.verbose == 1:
        verbosity = logging.CRITICAL
        vmsg = "Only found forms"
    elif args.verbose == 2:
        verbosity = logging.WARNING
        vmsg = "All crawled sites"
    else:
        verbosity = logging.DEBUG
        vmsg = "Granular logging"

    print_banner(args.url, args.depth, vmsg, args.verbose, args.same_domain, args.output)

    setupLogger(verbosity, args.output)

    find_forms(args.url, args.depth-1, args.same_domain)
