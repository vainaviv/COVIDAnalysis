import matplotlib.pyplot as plt 
import os
import re
from datetime import datetime
import numpy as np
import pandas as pd
from github import Github
import validators 
from svn.remote import RemoteClient

directory_path = "/Users/vainaviv/Desktop/ResearchSpring2020/COVIDAnalysis/COVID-19/csse_covid_19_data/csse_covid_19_daily_reports/"
Italy_deaths = []
Italy_days = []
California_deaths = []
California_days = []
Italy_start = ""
CA_start = ""
ca_found_start = False

italy_found_start = False

# PULL DATA FROM GITHUB : BEGIN

ACCESS_TOKEN = '25c7e7d67836ebf27849baf693accabaf5269659' 
g = Github(ACCESS_TOKEN)
print(g.get_user().get_repos())

url = input('https://github.com/CSSEGISandData/COVID-19/tree/master/csse_covid_19_data/csse_covid_19_daily_reports')

if not validators.url(url):
	print("invalid URL")
else:
	pass

def download_folder(url):
	if 'tree/master' in url:
		url = url.replace('tree/master', 'trunk')
	r = RemoteClient(url)
	r.export('output')

if not validators.url(url):
	print("invalid URL")
else:
	download_folder(url)

# PULL DATA FROM GITHUB : END

# SORT FILES BY DATE : BEGIN

def sortMethod(fileName):
	match = re.search(r"\d{2}-\d{2}-\d{4}", fileName)
	if (match):
		date = datetime.strptime(match.group(), "%m-%d-%Y").date()
		return date
	else :
		return datetime(3000,1,1).date()

dir_files = os.listdir(directory_path)
dir_files = sorted(dir_files, key = lambda row : sortMethod(row))

# SORT FILES BY DATE : END

# EXTRACT DATA POINTS : BEGIN

def Italy_parser(line):
	global italy_found_start, Italy_start
	if ("Italy" in line): 
		data = re.split(",", line)
		match = re.search(r"\d{4}-\d{2}-\d{2}", data[2])
		if (match):
			date = datetime.strptime(match.group(), "%Y-%m-%d").date()
		if italy_found_start:
			diff = date - Italy_start
			Italy_days.append(diff.days)
			Italy_deaths.append((int)(data[3]))
		if (int)(data[3]) >= 10 and (not Italy_deaths): #if it is empty
			Italy_start = date
			italy_found_start = True
			Italy_days.append(0)
			Italy_deaths.append((int)(data[3]))

def CA_parser(line): 
	global ca_found_start, CA_start
	if ("California" in line): 
		data = re.split(",", line)
		match = re.search(r"\d{4}-\d{2}-\d{2}", data[2])
		if (match):
			date = datetime.strptime(match.group(), "%Y-%m-%d").date()
		if ca_found_start:
			diff = date - CA_start
			California_days.append(diff.days)
			California_deaths.append((int)(data[3]))
		if (int)(data[3]) >= 10 and (not California_deaths): #if it is empty
			CA_start = date
			ca_found_start = True
			California_days.append(0)
			California_deaths.append((int)(data[3]))


for filename in dir_files:
	if filename.endswith(".csv"):
		file = open(directory_path + filename, "r")
		lines = file.readlines();
		for line in lines:
			Italy_parser(line)
			CA_parser(line)

# EXTRACT DATA POINTS : END
			
# LINEAR REGRESSION : BEGIN

last3daysCA = California_days[-3:]
last3deathsCA = California_deaths[-3:]

def best_fit(X, Y):
    xbar = sum(X)/len(X)
    ybar = sum(Y)/len(Y)
    n = len(X) # or len(Y)

    numer = sum([xi*yi for xi,yi in zip(X, Y)]) - n * xbar * ybar
    denum = sum([xi**2 for xi in X]) - n * xbar**2

    b = numer / denum
    a = ybar - b * xbar

    #print('best fit line:\ny = {:.2f} + {:.2f}x'.format(a, b))

    return a, b

# solution
a, b = best_fit(last3daysCA, last3deathsCA)
extraploate = list(range((int)(last3daysCA[2]) + 1, len(Italy_days)))
xfit = last3daysCA + extraploate
yfit = [a + b * xi for xi in xfit]
plt.plot(xfit, yfit)

print(last3deathsCA)
standard_deviation = np.std(last3deathsCA)
ytop = [y + standard_deviation for y in yfit]
ybottom = [y - standard_deviation for y in yfit]

# LINEAR REGRESSION : END 

# PLOT GRAPH : BEGIN

plt.fill_between(xfit, ybottom, ytop, facecolor = "lightskyblue")			

plt.semilogy(Italy_days, Italy_deaths, label = "Italy")
plt.semilogy(California_days, California_deaths, label = "California")
plt.legend(loc = "upper left")
plt.title('California vs. Italy')
#plt.yticks(np.arange(10, 5000, step = 500))
plt.xlabel("Number of days since 10th death")
plt.ylabel("Number of deaths")
plt.show()

# PLOT GRAPH : END 
