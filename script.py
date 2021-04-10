import re
from glob import glob
try:
	import pdfplumber
except:
	# install pdfplumber module to open and analyze pdf files
	import subprocess
	import sys
	subprocess.check_call([sys.executable, "-m", "pip", "install", "pdfplumber"])
	
	import pdfplumber

# directory where your statements are
dir = './'

"""
Files should be in dir in the format:
{dir}/2004_statement.pdf
{dir}/2005_statement.pdf
{dir}/2006_statement.pdf
{dir}/2007_statement.pdf
{dir}/2008_statement.pdf
"""

# The pattern for matching the transactions lines (BUY, SELL, DIV, ...)
line_re = re.compile(r'\d{2}/\d{2}/\d{4} \d{2}/\d{2}/\d{4}')

tickers = {}
others = []
dividend = 0
CDEP = 0
CSD = 0

def get_float(f):
	return float(f.replace('(','').replace(')','').replace(',',''))

def process_file(file):
	global dividend,CDEP, CSD
	with pdfplumber.open(file) as pdf:
		pages = pdf.pages

		for page in pages:
			text = page.extract_text()
			for line in text.split('\n'):
				if line_re.search(line):
					# print(line)
					parts = line.split()
					op = parts[3]
					amount = get_float(parts[-1])
					if op in ['BUY','SELL']:
						ticker = parts[4]
						qte = get_float(parts[-3])
						price = get_float(parts[-2])
						# print(f'{op} - {ticker} - {qte} - {price} - {amount}')
						if ticker not in tickers:
							tickers[ticker] = (qte, price, 0)
						else:
							prev_qte, prev_price, gain = tickers[ticker]
							new_qte = prev_qte + qte
							if qte > 0: # buy
								new_price = (prev_qte*prev_price + qte*price) / new_qte
							else: # sell
								assert new_qte >= -1e-3, new_qte
								gain -= qte*(price-prev_price)
								new_price = prev_price

							tickers[ticker] = (new_qte, new_price, gain)
					else:
						if op == 'DIV':
							dividend += amount
						elif op == 'DIVNRA':
							dividend -= amount
						elif op == 'CDEP':
							CDEP += amount
						elif op == 'CSD':
							CSD += amount
						else:
							1
							# print(f'{op} - {amount}')

for file in sorted(glob(dir+'*.pdf')):
	print(file)
	process_file(file)


total_gain = 0
for ticker, (qte, price, gain) in tickers.items():
	total_gain += gain

print(f'Total Gain/Loss: {total_gain:0.3f}')
print(f'Total Dividends: {dividend}')



