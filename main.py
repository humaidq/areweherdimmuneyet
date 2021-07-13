import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import sys
import math
from datetime import date, timedelta, datetime
import requests
from quik import FileLoader

# Doses goal for calculations
UAE_POP = 9890620
R0 = 6.5
GOAL = (1 - (1/R0))*100
print("goal", GOAL)

owid = pd.read_csv('data.csv')

dat = [ ] 

for index, row in owid.iterrows():
    fully = row['people_fully_vaccinated']
    if not math.isnan(fully):
        dat.append([row['date'], (fully/UAE_POP)*100])

dataset = pd.DataFrame(dat, columns=['Date', 'Percentage'])
dataset['Date'] = pd.to_datetime(dataset['Date'])

x = mdates.date2num(pd.Index(dataset.Date).to_pydatetime())
y = dataset['Percentage']


def get_herd_immunity():
    model = np.poly1d(np.polyfit(x, y, 2))
    x0 = (model - GOAL).roots
    #print(mdates.num2date(x0[0]), mdates.num2date(x[1]))
    return (model, mdates.num2date(x0[1]))


def gen_html(estimate):
    print("Rendering HTML")
    loader = FileLoader('.')
    template = loader.load_template('template.html')
    estimate_txt = estimate.strftime("%d %B")
    res = template.render(
        {'estimate': estimate_txt,
         'goalMs': round(estimate.timestamp()),
         'today': date.today().strftime("%d %B"),
         'ver': round(datetime.now().timestamp()),
         'goal': int(GOAL)},
        loader=loader).encode('utf-8')
    f = open("index.html", "w")
    f.write(res.decode("utf-8"))
    f.close()


def gen_img():
    print("Generating image")
    model, estimate = get_herd_immunity()
    estimate_txt = estimate.strftime("%d %b")

    # show graph up to:
    until = estimate + timedelta(days=3)
    myline = np.linspace(mdates.date2num(dataset.Date[0]),
                         mdates.date2num(until))

    fig, ax = plt.subplots()

    # set color to match page
    fig.set_facecolor("#fafafa")

    dayloc = mdates.DayLocator()
    fdloc = mdates.DayLocator(interval=15)
    maj_fmt = mdates.DateFormatter('%-d %b')
    ax.xaxis.set_major_formatter(maj_fmt)
    ax.xaxis.set_major_locator(fdloc)
    ax.xaxis.set_minor_locator(dayloc)
    fig.autofmt_xdate()
    ax.grid(True)
    ax.grid(b=True, which="minor")

    plt.plot(dataset.Date, y, label="People fully vaccinated",
             color="tab:green")
    plt.plot(myline, model(myline), label="Estimate (polynomial regression)",
             linestyle=":", color="tab:orange")
    plt.plot(mdates.date2num(estimate), GOAL, 'g*',
            label="Estimated Goal ("+str(int(GOAL))+"%)")
    plt.text(mdates.date2num(estimate)-15, GOAL-2, "("+estimate_txt+")")
    plt.ylabel('Percentage')
    plt.xlabel('Date')
    plt.title('People Fully Vaccinated')
    plt.legend()

    ax.tick_params(axis='x', which='both', labelsize=5)
    plt.savefig('chart.svg')

    print("We will reach herd immunity at: " + estimate_txt)
    gen_html(estimate)

if __name__ == "__main__":
    gen_img()
