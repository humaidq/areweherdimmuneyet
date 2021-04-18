import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import sys
from datetime import date, timedelta, datetime
import requests
from quik import FileLoader

# Doses goal for calculations
DOSES_GOAL = 120

dataset = pd.read_csv('data.csv')
dataset['Date'] = pd.to_datetime(dataset['Date'])

x = mdates.date2num(pd.Index(dataset.Date).to_pydatetime())
y = dataset['Doses']


def get_herd_immunity():
    model = np.poly1d(np.polyfit(x, y, 1))
    x0 = (model - DOSES_GOAL).roots
    # print(mdates.num2date(x0[0]), mdates.num2date(x[1]))
    return (model, mdates.num2date(x0[0]))


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
         'goal': DOSES_GOAL,
         'perc': int((DOSES_GOAL/200)*100)},
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
    fdloc = mdates.DayLocator(interval=5)
    maj_fmt = mdates.DateFormatter('%-d %b')
    ax.xaxis.set_major_formatter(maj_fmt)
    ax.xaxis.set_major_locator(fdloc)
    ax.xaxis.set_minor_locator(dayloc)
    fig.autofmt_xdate()
    ax.grid(True)
    ax.grid(b=True, which="minor")

    plt.plot(dataset.Date, y, label="Inoculations per 100 people",
             color="tab:green")
    plt.plot(myline, model(myline), label="Estimate (linear regression)",
             linestyle=":", color="tab:orange")
    plt.plot(mdates.date2num(estimate), DOSES_GOAL, 'g*',
             label="Estimated Goal (120 doses)")
    plt.text(mdates.date2num(estimate)-15, DOSES_GOAL-2, "("+estimate_txt+")")
    plt.ylabel('Doses')
    plt.xlabel('Date')
    plt.title('COVID-19 Vaccine Doses per 100')
    plt.legend()

    # horizontal line
    # plt.axhline(y=DOSES_GOAL, color='r', linestyle=':')

    ax.tick_params(axis='x', which='both', labelsize=5)
    plt.savefig('chart.svg')

    print("We will reach herd immunity at: " + estimate_txt)
    gen_html(estimate)


def pull_data():
    api = "http://covid19.ncema.gov.ae/ar/Home/InitializeDosesLineChart"
    params = dict(
            Year=0,
            Month=0,
            Type="LatestTenDays",
            screenWidth=1080,
    )

    resp = requests.post(url=api, json=params, verify=False)
    data = resp.json()
    dataset = data['ChartDataSets'][0]["data"]
    latest_doses = dataset[len(dataset)-1]

    d = date.today().strftime("%Y-%m-%d")
    entry = d+","+latest_doses
    print(entry)
    conf = input("Do you want to add this entry (y/n)? ")
    if conf == "y":
        f = open("data.csv", "a")
        f.write(entry+"\n")
        f.close()
        gen_img()


def main():
    if len(sys.argv) == 1:
        print("usage: ./awhiy <OPTION>\n")
        print("OPTIONS:")
        print("\tgen: generate a new graph image (SVG)")
        print("\tpull: pull latest vaccine doses entry from NCEMA")
    if sys.argv[1] == "gen":
        gen_img()
    elif sys.argv[1] == "pull":
        pull_data()


if __name__ == "__main__":
    main()
