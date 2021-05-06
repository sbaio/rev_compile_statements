#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
    A simple script to compile the monthly statements provided by Revolut for trading history.
    It provides the total gain/loss and the total dividend from downloaded pdf statements.
"""

import re
from glob import glob
try:
    import pdfplumber
except ImportError:
    # install pdfplumber module to open and analyze pdf files
    import subprocess
    import sys
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pdfplumber"])

    import pdfplumber

# directory where your statements are
BASE_DIR = './'

"""
Files should be in dir in the format:
{BASE_DIR}/2004_statement.pdf
{BASE_DIR}/2005_statement.pdf
{BASE_DIR}/2006_statement.pdf
{BASE_DIR}/2007_statement.pdf
{BASE_DIR}/2008_statement.pdf
"""

# The pattern for matching the transactions lines (BUY, SELL, DIV, ...)
LINE_RE = re.compile(r'\d{2}/\d{2}/\d{4} \d{2}/\d{2}/\d{4}')

TICKERS = {}
OTHERS = []
DIVIDEND = 0
CDEP = 0
CSD = 0


def get_float(string):
    """Get float function"""
    return float(string.replace('(', '').replace(')', '').replace(',', ''))


def process_file(file):
    """Main process that read all files"""
    global DIVIDEND, CDEP, CSD
    with pdfplumber.open(file) as pdf:
        pages = pdf.pages

        for page in pages:
            text = page.extract_text()
            for line in text.split('\n'):
                if LINE_RE.search(line):
                    # print(line)
                    parts = line.split()
                    OP = parts[3]
                    amount = get_float(parts[-1])
                    if OP in ['BUY', 'SELL']:
                        ticker = parts[4]
                        qte = get_float(parts[-3])
                        price = get_float(parts[-2])
                        # print(f'{OP} - {ticker} - {qte} - {price} - {amount}')
                        if ticker not in TICKERS:
                            TICKERS[ticker] = (qte, price, 0)
                        else:
                            prev_qte, prev_price, gain = TICKERS[ticker]
                            new_qte = prev_qte + qte
                            if qte > 0:  # buy
                                new_price = (prev_qte*prev_price + qte*price) / new_qte
                            else:  # sell
                                assert new_qte >= -1e-3, new_qte
                                gain -= qte*(price-prev_price)
                                new_price = prev_price

                            TICKERS[ticker] = (new_qte, new_price, gain)
                    else:
                        if OP == 'DIV':
                            DIVIDEND += amount
                        elif OP == 'DIVNRA':
                            DIVIDEND -= amount
                        elif OP == 'CDEP':
                            CDEP += amount
                        elif OP == 'CSD':
                            CSD += amount
                        else:
                            1
                            # print(f'{OP} - {amount}')

global file
for file in sorted(glob(BASE_DIR+'*.pdf')):
    print(file)
    process_file(file)


TOTAL_GAIN = 0
for ticker, (qte, price, gain) in TICKERS.items():
    TOTAL_GAIN += gain

print(f'Total Gain/Loss: {TOTAL_GAIN:0.3f}')
print(f'Total Dividends: {DIVIDEND}')
