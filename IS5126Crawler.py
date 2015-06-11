from urllib import urlopen
from bs4 import BeautifulSoup
from bs4 import SoupStrainer
import re
import csv
import time
import string 


#Appends www.basketball-reference.com to the url 
def url_generator(url):
	return ("http://basketball-reference.com"+url)

#To generate urls that contain lists of players sorted by last name
def gen_start_url(start_urls):
	allLetters = string.lowercase
	for letter in allLetters:
		if letter == 'x':
			continue
		start_urls.append('/players/'+letter+'/')
		
#Opens csv output files in append mode, and returns file object. Team.csv if case is team, else based on table id attribute
def csv_generator(case, id):
	if case == 'team':
		file = open(case+'.csv','a')
	else:
		file = open(id+'.csv','a')
	return file

#Fills basic and transaction history of a player	
def fill_basic_info(soup):	
	info_items = ['Name:','Position:','Shoots:','Height:','Weight:','Born:','Hall of Fame:']
	trans_items = ['Player','Date','By','To']
	info_file = open('basic_info.csv','a')
	trans_file = open('transaction_history.csv','a')
	
	div = soup.find('div',{'id':'info_box'})
	spans = div.find_all('span',{'class':'bold_text'})
	info_file.write(soup.h1.get_text()+',')
	for span in spans:
		value = span.get_text()
		if value == info_items[5]:
			if span.next_sibling.next_sibling.get('data-birth'):
				info_file.write(span.next_sibling.next_sibling.get('data-birth').strip()+',')
		elif value == info_items[6]:
			info_file.write(span.next_sibling.strip().lstrip('Inducted as Player in').rstrip(' (')+',')
		elif span.get_text() in info_items[ :5]:
			info_file.write(span.next_sibling.replace(',','').encode('ASCII','ignore').strip()+',')
	info_file.write('\n')
	info_file.close()
	
	trans = soup.find('div',{'id':'transactions'})
	if trans:
		if 'Traded' in trans.get_text():
			paras = trans.find_all('p')
			for para in paras:
				if 'Traded' in para.get_text():
					trans_file.write(soup.h1.get_text()+',')
					trans_file.write(para.find('span',{'class':'bold_text'}).get_text().replace(',','')+',')
					links = para.find_all('a',{'href':re.compile('/teams/')})
					for link in links:
						trans_file.write(link.get_text()+',')
				trans_file.write('\n')	
		trans_file.close()
		
#Puts in Headers in the csv file. Based on case (team/player). If player, a Player Name field is also added				
def header_write(link, case):
	soup = BeautifulSoup(urlopen(url_generator(link.get('href'))))
	print "Header for " + link.get_text()
	for table in soup.findAll("table",{"class":re.compile(r"^sortable")}):
		out = csv_generator(case, table.get('id'))
		if case == 'player':
			out.write('Player Name,')
		headerData = table.findAll("th")
		for item in headerData:
			if item.get_text():
				out.write(item.get_text()+",")
		out.write("\n")
	out.close()

#Gets statistics tables, and writes into output csv. Accepts list of links (to player and team pages) and case as argument
def stats_extractor(links, case):
	for link in links:
		print "Iteration for " + link.get_text()
		soup = BeautifulSoup(urlopen(url_generator(link.get('href'))))
		player_name = link.get_text()
		time.sleep(3)
		if case == 'player':
			fill_basic_info(soup)
		#finds all tables whose class starts with the word "sortable"
		for table in soup.findAll("table",{"class":re.compile(r"^sortable")}): 
			opens appropriate output file based on team/player
			out = csv_generator(case, table.get('id'))
			for row in table.tbody.findAll('tr'):
				if case == 'player':
					out.write(player_name+',')
				for col in row.findAll('td'): 
					out.write(col.get_text().replace(',','').encode('ASCII','ignore')+',')
				out.write('\n')
			out.close()
			


start_urls = ['/teams/']
gen_start_url(start_urls)

info_file = csv_generator('basic_info')
trans_file = csv_generator('transaction_info')

#Get first team page to create output file and generate table headers
team_links_only = SoupStrainer('a',{"href":re.compile(start_urls[0])})
soup = BeautifulSoup(urlopen(url_generator(start_urls[0])), parse_only = team_links_only)
team_links = soup.find_all('a')
# Removes first link from list (it is www.basketball-reference.com/teams/)
team_links.pop(0)
header_write(team_links[0],'team')
get stats for teams
stats_extractor(team_links, 'team')

# ditto for player
player_links_only = SoupStrainer('a',{"href":re.compile(start_urls[1])})
soup = BeautifulSoup(urlopen(url_generator(start_urls[1])), parse_only = player_links_only)
player_links = soup.find('a')
header_write(player_links,'player')

#get stats for player
for start_url in start_urls[2:]: 
	links = SoupStrainer('a',{"href":re.compile(start_url)})
	soup = BeautifulSoup(urlopen(url_generator(start_url)), parse_only = links)
	links = soup.find_all('a')
	stats_extractor(links,'player')
	
	
	