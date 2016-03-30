from datetime import date, timedelta, datetime
import collections
import csv
import myfitnesspal
import json
import plotly
import plotly.graph_objs as go
import yaml

# Brian Cain 2016
# A simple python script to get myfitnesspal data
# and do some simple analysis on it.

def macros_barchart(data):
    # X axis is date
    # Y axis is macro nutrients
    x_axis = []
    y_protein = []
    y_carbs = []
    y_fat = []

    for d in data:
        x_axis.append(d.date)
        if 'protein' in d.totals:
            y_protein.append(d.totals['protein'])
        else:
            y_protein.append(0)
        if 'carbohydrates' in d.totals:
            y_carbs.append(d.totals['carbohydrates'])
        else:
            y_carbs.append(0)
        if 'fat' in d.totals:
            y_fat.append(d.totals['fat'])
        else:
            y_fat.append(0)

    protein = go.Bar(
            x = x_axis,
            y = y_protein,
            name = 'Protein')

    carbs = go.Bar(
            x = x_axis,
            y = y_carbs,
            name = 'Carbohydrates')

    fat = go.Bar(
            x = x_axis,
            y = y_fat,
            name = 'Fat')

    total_data = [protein, carbs, fat]
    layout = go.Layout(barmode='stack')
    figure = go.Figure(data=total_data, layout=layout)
    plotly.offline.plot(figure, filename='graphs/stacked-bar-macros.html')

def macros_piechart(data):
    total_protein = 0
    total_carbs = 0
    total_fat = 0

    for d in data:
        if 'protein' in d.totals:
            total_protein += d.totals['protein']
        if 'carbohydrates' in d.totals:
            total_carbs += d.totals['carbohydrates']
        if 'fat' in d.totals:
            total_fat += d.totals['fat']

    avg_protein = total_protein / len(data)
    avg_carbs = total_carbs / len(data)
    avg_fat = total_fat / len(data)

    figure = {
        'data': [{'labels': ['Protein', 'Carbohydrates', 'Fat'],
                  'values': [avg_protein, avg_carbs, avg_fat],
                  'type': 'pie'}],
        'layout': {'title': 'Average macro nutrients'}
    }

    plotly.offline.plot(figure, filename='graphs/avg-macro-pie.html')

def total_calories_chart(data):
    x_axis = []
    y_axis = []

    for d in data:
        x_axis.append(d.date)
        if 'calories' in d.totals:
            y_axis.append(d.totals['calories'])
        else:
            y_axis.append(0)

    data = [go.Scatter(x=x_axis, y=y_axis)]
    plotly.offline.plot(data, filename='graphs/calories-series.html')

def weight_chart(weight):
    x_axis = weight.keys()
    y_axis = weight.values()

    data = [go.Scatter(x=x_axis, y=y_axis)]
    plotly.offline.plot(data, filename='graphs/weight-series.html')

def lifting_vs_weight_chart(weight, deadlift_data, bench_data, squat_data):
    # https://plot.ly/python/multiple-axes/
    x_weight = weight.keys()
    y_weight = weight.values()

    x_deadlift = []
    y_deadlift = []
    x_bench = []
    y_bench = []
    x_squat = []
    y_squat = []

    for d in sorted(deadlift_data):
        x_deadlift.append(d)
        y_deadlift.append(deadlift_data[d])

    for d in sorted(squat_data):
        x_squat.append(d)
        y_squat.append(squat_data[d])

    for d in sorted(bench_data):
        x_bench.append(d)
        y_bench.append(bench_data[d])

    weights = go.Scatter(
            x = x_weight,
            y = y_weight,
            name = 'Body Weight')

    deadlifts = go.Scatter(
            x = x_deadlift,
            y = y_deadlift,
            name = 'Deadlift Top Sets',
            yaxis = 'y2')

    benches = go.Scatter(
            x = x_bench,
            y = y_bench,
            name = 'Bench Top Sets',
            yaxis = 'y3')

    squats = go.Scatter(
            x = x_squat,
            y = y_squat,
            name = 'Squat Top Sets',
            yaxis = 'y4')

    total_data = [weights,deadlifts,benches,squats]

    layout = go.Layout(
            title = 'Weight vs Powerlifting over time',
            yaxis = dict(title='Body Weight',
                         titlefont=dict(color='#1f77b4'),
                         tickfont=dict(color='#1f77b4')),
            yaxis2 = dict(
                title='Deadlift Top Sets',
                titlefont=dict(color='#ff7f0e'),
                tickfont=dict(color='#ff7f0e'),
                overlaying='y',
                side='left',
                position=0.05),
            yaxis3 = dict(
                title='Bench Top Sets',
                titlefont=dict(color='#006400'),
                tickfont=dict(color='#006400'),
                anchor='free',
                overlaying='y',
                side='right',
                position=0.95),
            yaxis4 = dict(
                title='Squat Top Sets',
                titlefont=dict(color='#d62728'),
                tickfont=dict(color='#d62728'),
                anchor='x',
                overlaying='y',
                side='right'))
    figure = go.Figure(data=total_data, layout=layout)
    plotly.offline.plot(figure, filename='graphs/weight-lift-series.html')

def weights_vs_cals_chart(data, weight):
    # https://plot.ly/python/multiple-axes/
    x_cals = []
    y_cals = []
    x_weight = weight.keys()
    y_weight = weight.values()

    for d in data:
        x_cals.append(d.date)
        if 'calories' in d.totals:
            y_cals.append(d.totals['calories'])
        else:
            y_cals.append(0)

    calories = go.Scatter(
            x = x_cals,
            y = y_cals,
            name = 'Calories')

    weights = go.Scatter(
            x = x_weight,
            y = y_weight,
            name = 'Body Weight',
            yaxis = 'y2')

    total_data = [calories,weights]

    layout = go.Layout(
            title = 'Weight vs Calories over time',
            yaxis = dict(title='Calories'),
            yaxis2 = dict(
                title='Body Weight',
                titlefont=dict(color='#1f77b4'),
                tickfont=dict(color='#1f77b4'),
                overlaying='y',
                side='right',
                position=.95))
    figure = go.Figure(data=total_data, layout=layout)
    plotly.offline.plot(figure, filename='graphs/weight-cals-series.html')

def get_data(mfp_client, start_date):
    d1 = start_date
    d2 = date.today()
    delta = d2 - d1
    data = []
    missed_dates = []

    print "Retrieving data from myfitnesspal....this will take a while...\n"
    for i in range(delta.days + 1):
        local_date = d1 + timedelta(days=i)
        print "Getting date " + str(local_date) + " . . ."

        # terribad try/catch because the myfitnesspal api is super unstable
        try:
            mfp_data = mfp_client.get_date(local_date)
        except IndexError as e:
            print e
            print "Could not get date . . . continuing anyway . . ."
            missed_dates.append(local_date)
            continue
        except:
            print "Something went wrong :("
            raise

        data.append(mfp_data)

    if len(missed_dates) > 0:
        print
        print "Could not get information for these dates:"
        print missed_dates
        print

    return data

def get_lifts(path):
    f = open(path, 'rb')
    column = 0
    d = {}

    try:
        reader = csv.reader(f, delimiter=',', quotechar='|')
        date = ''
        for row in reader:
            date = datetime.strptime(row[1], "%Y-%m-%d").strftime("%Y-%m-%d")
            weight = float(row[3])
            if date in d:
                if d[date] < weight:
                    d[date] = weight
            else:
                d[date] = weight

    finally:
        f.close()

    return d

def get_login():
    with open("login.yaml", "r") as stream:
        try:
            login_info = yaml.load(stream)
            return login_info
        except yaml.YAMLError as exc:
            print exc
            exit(1)

def generate_charts(data, body_weights, deadlift_data, bench_data, squat_data):
    print "Generating charts . . ."
    macros_barchart(data)
    total_calories_chart(data)
    weights_vs_cals_chart(data, body_weights)
    lifting_vs_weight_chart(body_weights, deadlift_data, bench_data, squat_data)
    weight_chart(body_weights)
    macros_piechart(data)

def save_mfp_data(data):
    with open('mfpdata.json', 'wb') as outfile:
            json.dump(data, outfile)

def main():
    login_info = get_login()
    #start_date = date(2013, 8, 31) # original start date on MFP
    start_date = date(2013, 7, 28) # first weight record, no meals
    #start_date = date(2016, 3, 25) # test date

    print "Logging in as " + login_info['username'] + "..."
    client = myfitnesspal.Client(login_info['username'], login_info['password'])
    print "Done!"

    body_weights = client.get_measurements('Weight', start_date)
    data = get_data(client, start_date)
    #save_mfp_data(data)

    deadlift_data = get_lifts("training/deadlifts.csv")
    bench_data = get_lifts("training/bench.csv")
    squat_data = get_lifts("training/squat.csv")


    generate_charts(data, body_weights, deadlift_data, bench_data, squat_data)

if __name__ == '__main__':
    main()
