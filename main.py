import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime

dataset = pd.read_csv('data.csv')
dataset['Date'] = pd.to_datetime(dataset['Date'])

x = mdates.date2num(pd.Index(dataset.Date).to_pydatetime())
y = dataset['Doses']

mymodel = np.poly1d(np.polyfit(x, y, 2))

# show graph up to:
until = datetime.strptime('2021-05-01', '%Y-%m-%d')
myline = np.linspace(mdates.date2num(dataset.Date[0]), mdates.date2num(until))

dayloc = mdates.DayLocator()
fdloc = mdates.DayLocator(interval=5)
fig, ax = plt.subplots()
maj_fmt = mdates.DateFormatter('%-d %b')
min_fmt = mdates.DateFormatter('%-d')
ax.xaxis.set_major_formatter(maj_fmt)
#ax.xaxis.set_minor_formatter(min_fmt)
ax.xaxis.set_major_locator(fdloc)
ax.xaxis.set_minor_locator(dayloc)
fig.autofmt_xdate()
ax.grid(True)
ax.grid(b=True, which="minor")

plt.plot(dataset.Date, y, label="Doses per 100", color="tab:green")
plt.plot(myline, mymodel(myline), label="Estimate (polynomial regression)",
         linestyle=":", color="tab:orange")
plt.ylabel('Doses')
plt.xlabel('Date')
plt.title('COVID-19 Vaccine Doses per 100')
plt.legend()

# horizontal line
plt.axhline(y = 120, color = 'r', linestyle = ':')

ax.tick_params(axis='x', which='both', labelsize=5)
plt.savefig('chart.svg')

d = datetime.strptime('2021-04-22', '%Y-%m-%d')
print("Doses will be: " + str(mymodel(mdates.date2num(d))))
print(mymodel(120))
