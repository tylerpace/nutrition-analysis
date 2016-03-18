from datetime import date, timedelta
import myfitnesspal
import yaml

# Brian Cain 2016
# A simple python script to get myfitnesspal data
# and do some simple analysis on it.

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

def main():
    login_info = get_login()
    #start_date = date(2013, 8, 31) # original start date on MFP
    start_date = date(2016, 3, 16)

    client = myfitnesspal.Client(login_info['username'], login_info['password'])

    body_weights = client.get_measurements('Weight', start_date)

    data = get_data(client, start_date)
    print data

if __name__ == '__main__':
    main()
