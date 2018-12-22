# (c) 2015 QuantAtRisk.com, by Pawel Lachowicz
# stolen from http://www.quantatrisk.com/2015/04/24/how-to-find-a-company-name-given-a-stock-ticker-symbol-utilising-quandl-api/
import pandas as pd
def find_ticker(ticker):
	df = pd.read_csv('secwiki_tickers.csv')
	test = df[df.Ticker==ticker]
	if not (test.empty):
		name = list(test.Name.values)[0]
		if "," in name: 
			name = name[:name.find(",")]
		elif "Corp" in name: 
			name = name[:name.find("Corp")]
		elif "Corporation" in name:
			name = name[:name.find("Corporation")]
		if "Inc" in name: 
			name = name[:name.find("Inc")]
		if "Incorporated" in name: 
			name = name[:name.find("Incorporated")]
		else: 
			pass 
		name = name.strip()
		return name
	else: 
		return None
