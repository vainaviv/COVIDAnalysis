import matplotlib.pyplot as plt 
import os
import re
from datetime import datetime
import numpy as np
import pandas as pd
import validators
import pygit2
import shutil
from pathlib import Path

Italy_deaths = []
Italy_days = []
California_deaths = []
California_days = []
Italy_start = ""
CA_start = ""
ca_found_start = False
italy_found_start = False
ca_death_index = 0
italy_death_index = 0

# PULL DATA FROM GITHUB : BEGIN

if os.path.exists('output'):
	print('Deleting old repository...')
	if os.name == 'nt':
		os.system('rd /s /q output')
	else:
		os.system('rm -rf output')

print('Cloning repository...')
pygit2.clone_repository('https://github.com/CSSEGISandData/COVID-19', 'output')
print('Cloned repository.')

directory_path = os.path.join(os.path.abspath('output'), 'csse_covid_19_data', 'csse_covid_19_daily_reports') + os.path.sep

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

def Italy_parser(line, date):
	global italy_found_start, Italy_start
	if ("Italy" in line): 
		data = re.split(",", line)
		match = re.search(r"\d{4}-\d{2}-\d{2}", data[2])
		if (match):
			date = datetime.strptime(match.group(), "%Y-%m-%d").date()
			if italy_found_start:
				diff = date - Italy_start
				if diff.days == 15:
					print(date)
				Italy_days.append(diff.days)
				Italy_deaths.append((int)(data[3]))
			if data[ca_death_index] != '' and (int)(data[italy_death_index]) >= 10 and (not Italy_deaths): #if it is empty
				Italy_start = date
				italy_found_start = True
				Italy_days.append(0)
				Italy_deaths.append((int)(data[3]))

def CA_parser(line, date): 
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
			if data[ca_death_index] != '' and (int)(data[ca_death_index]) >= 10 and (not California_deaths): #if it is empty
				CA_start = date
				ca_found_start = True
				California_days.append(0)
				California_deaths.append((int)(data[3]))


for filename in dir_files:
	ca_death_index = 0
	italy_death_index = 0
	if filename.endswith(".csv"):
		file_date = sortMethod(filename)
		file = open(directory_path + filename, "r")
		lines = file.readlines();
		for line in lines:
			l = re.split(",", line)
			if ca_death_index == 0:
				ca_death_index = l.index("Deaths")
			if italy_death_index == 0:
				italy_death_index = l.index("Deaths")
			Italy_parser(line,file_date)
			CA_parser(line, file_date)

# EXTRACT DATA POINTS : END
			
# LINEAR REGRESSION : BEGIN

last3daysCA = California_days[-3:]
last3deathsCA = California_deaths[-3:]
print(last3deathsCA)
print(last3daysCA)

def best_fit(X, Y):
    xbar = sum(X)/len(X)
    ybar = sum(Y)/len(Y)
    n = len(X) # or len(Y)

    numer = sum([xi*yi for xi,yi in zip(X, Y)]) - n * xbar * ybar
    denum = sum([xi**2 for xi in X]) - n * xbar**2

    b = numer / denum
    a = ybar - b * xbar

    return a, b

a, b = best_fit(last3daysCA, last3deathsCA)
extraploate = list(range((int)(last3daysCA[2]), len(Italy_days)))
xfit = extraploate
yfit = [a + b * xi for xi in xfit]
plt.plot(xfit, yfit)

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
plt.xlabel("Number of days since 10th death")
plt.ylabel("Number of deaths")
plt.savefig("ItalyvCA.png")

# PLOT GRAPH : END 
