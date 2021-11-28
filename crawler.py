
import json
import requests
import time
import calendar
import csv
import os

# https://www.wunderground.com/
ApiKey = os.getenv('API_KEY', 'get_your_api_key')


Start_Year = 2017
Years_To_Include = 4
Keys_To_Remain = [
    "obs_name", "day_ind", "temp",
    "wx_phrase", "dewPt", "wdir_cardinal",
    "uv_desc"
]


def get_file_name(years: list) -> str:
    fmt = "{0}_to_{1}_run_at_{2}.csv"
    time_stamp = time.strftime("%Y-%m-%d-%H:%M:%S", time.localtime())
    file_name = fmt.format(years[0], years[-1], time_stamp)
    return file_name


def get_last_day(year, month):
    lastday = calendar.monthrange(year, month)
    return lastday


def get_date_range(years: list) -> list:
    """
    Get date ranges for the given years by month period. 

    Returns a list of date pair like (1st_day_of_month, last_day_of_month)
    [(20210101, 20210131), ...]
    """
    dates = []
    months = range(1, 12)
    fmt = "{0}{1:02d}{2}"

    for year in years:
        for month in months:
            last_day = get_last_day(year, month)[1]
            start = fmt.format(year, month, '01')
            end = fmt.format(year, month, last_day)
            dates.append((start, end))
    return dates


def download_demo(url):
    response = requests.get(url)
    text = response.text
    print(type(text))
    data = json.loads(text)
    user = data[0]
    print(user['name'])
    address = user['address']
    print(address)


def compose_url(datePair):
    apiKey = ApiKey
    baseUrl = 'https://api.weather.com/v1/location/ZLXY:9:CN/observations/historical.json'
    fmt = '{baseUrl}?apiKey={apiKey}&units=e&startDate={start}&endDate={end}'
    return fmt.format(baseUrl=baseUrl, apiKey=apiKey, start=datePair[0], end=datePair[1])


def download_weather_data(url) -> list:
    resp = requests.get(url)
    if resp.status_code != 200:
        raise "Http Request failed with code:{0}".format(resp.status_code)
    json_data = json.loads(resp.text)
    items = json_data['observations']
    data = map(convert_data_to_expected_shape, items)
    return list(data)


def convert_data_to_expected_shape(json_obj: dict):
    timestamp = json_obj["valid_time_gmt"]
    time = convert_to_datetime(timestamp)

    F = json_obj["temp"]
    C = fahrenheit_to_celsius(F)

    remains = {k: v for k, v in json_obj.items() if k in Keys_To_Remain}

    update = json.dumps(
        {**remains, **{"date_time": time, "temp_centigrade": C}})
    new = json.loads(update)
    return new


def convert_to_datetime(timestamp: int):
    timestr = time.localtime(timestamp)
    return time.strftime("%Y-%m-%d %H:%M:%S", timestr)


def fahrenheit_to_celsius(fahrenheit: int):
    if isinstance(fahrenheit, (int, float)) and not isinstance(fahrenheit, bool):
        celsius = (fahrenheit - 32) / 1.8
        return round(celsius, 2)
    else:
        return -100


def get_years_range(start: int, years_to_include: int = 0) -> list:
    """
    Get {years_to_include} years from the start year
    0 to return the start year only
    """
    years_range = range(start, start + years_to_include + 1)
    return [*years_range]


def run():
    years_to_download = get_years_range(Start_Year, Years_To_Include)
    file_name = get_file_name(years_to_download)
    print("years to download:", years_to_download)
    print("save file to:", file_name)
    with open(file_name, 'a+', newline='') as csv_file:
        writer = csv.writer(csv_file)
        dateRange = get_date_range(years_to_download)
        for datePair in dateRange:
            print("processing {} ...".format(datePair))
            url = compose_url(datePair)
            data = download_weather_data(url)
            is_header_row = True
            for temp_item in data:
                if is_header_row:
                    header = temp_item.keys()
                    writer.writerow(header)
                    is_header_row = False
                writer.writerow(temp_item.values())
            time.sleep(3)
        csv_file.close()


if __name__ == '__main__':

    run()

    print("done...")
