from datetime import date, timedelta
import csv
import myfitnesspal
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
        y_protein.append(d.totals['protein'])
        y_carbs.append(d.totals['carbohydrates'])
        y_fat.append(d.totals['fat'])

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
        total_protein += d.totals['protein']
        total_carbs += d.totals['carbohydrates']
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
        y_axis.append(d.totals['calories'])

    data = [go.Scatter(x=x_axis, y=y_axis)]
    plotly.offline.plot(data, filename='graphs/calories-series.html')

def weight_chart(weight):
    x_axis = weight.keys()
    y_axis = weight.values()

    data = [go.Scatter(x=x_axis, y=y_axis)]
    plotly.offline.plot(data, filename='graphs/weight-series.html')

def weights_vs_cals_chart(data, weight):
    # https://plot.ly/python/multiple-axes/
    x_cals = []
    y_cals = []
    x_weight = weight.keys()
    y_weight = weight.values()

    for d in data:
        x_cals.append(d.date)
        y_cals.append(d.totals['calories'])

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
                titlefont=dict(color='rgb(148, 103, 189)'),
                tickfont=dict(color='rgb(148, 103, 189)'),
                overlaying='y',
                side='right'))
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
            print ', '.join(row)
            column++
    finally:
        f.close()

def get_login():
    with open("login.yaml", "r") as stream:
        try:
            login_info = yaml.load(stream)
            return login_info
        except yaml.YAMLError as exc:
            print exc
            exit(1)

def generate_charts(data, body_weights):
    print "Generating charts . . ."
    macros_barchart(data)
    total_calories_chart(data)
    weights_vs_cals_chart(data, body_weights)
    weight_chart(body_weights)
    macros_piechart(data)

def main():
    login_info = get_login()
    #start_date = date(2013, 8, 31) # original start date on MFP
    #start_date = date(2013, 7, 28) # first weight record, no meals

    start_date = date(2015, 1, 1)

    print "Logging in as " + login_info['username'] + "..."
    client = myfitnesspal.Client(login_info['username'], login_info['password'])
    print "Done!"

    body_weights = client.get_measurements('Weight', start_date)
    data = get_data(client, start_date)

    #deadlift_data = get_lifts("training/deadlifts.csv")

    generate_charts(data, body_weights)

if __name__ == '__main__':
    main()
