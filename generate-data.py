from datetime import date, timedelta
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
            name = 'Total weight',
            yaxis = 'y2')

    total_data = [calories, weights]

    layout = go.Layout(
            title = 'Weight vs Calories over time',
            yaxis = dict(title='Calories'),
            yaxis2 = dict(
                title = 'Weight',
                titlefont = dict(color='rgb(148, 103, 189)'),
                tickfont = dict(color='rgb(148, 103, 189)'),
                overlaying = 'y',
                side = 'right'))
    plotly.offline.plot(total_data, filename='graphs/weight-cals-series.html')

def get_data(mfp_client, start_date):
    d1 = start_date
    d2 = date.today()
    delta = d2 - d1

    data = []

    # build up a list of dates and meals from beginning to today
    # ...this is gonna take a while...
    print "Retrieving data from myfitnesspal....this will take a while..."
    for i in range(delta.days + 1):
        mfp_data = mfp_client.get_date(d1 + timedelta(days=i))
        data.append(mfp_data)

    return data

def get_login():
    with open("login.yaml", "r") as stream:
        try:
            login_info = yaml.load(stream)
            return login_info
        except yaml.YAMLError as exc:
            print exc
            exit(1)

def generate_charts(data, body_weights):
    macros_barchart(data)
    total_calories_chart(data)
    weights_vs_cals_chart(data, body_weights)
    #weight_chart(body_weights)

def main():
    login_info = get_login()
    #start_date = date(2013, 8, 31) # original start date on MFP
    #start_date = date(2013, 7, 28) # first weight record, no meals

    start_date = date(2016, 1, 1)

    client = myfitnesspal.Client(login_info['username'], login_info['password'])

    body_weights = client.get_measurements('Weight', start_date)

    data = get_data(client, start_date)

    generate_charts(data, body_weights)

if __name__ == '__main__':
    main()
