import unittest
import crawler
import json


class TestCrawler(unittest.TestCase):

    def test_date_range(self):
        expected = [('20210101', '20210131'),
                    ('20210201', '20210228'),
                    ('20210301', '20210331'),
                    ('20210401', '20210430'),
                    ('20210501', '20210531'),
                    ('20210601', '20210630'),
                    ('20210701', '20210731'),
                    ('20210801', '20210831'),
                    ('20210901', '20210930'),
                    ('20211001', '20211031'),
                    ('20211101', '20211130')]
        dates = crawler.get_date_range([2021])
        self.assertEqual(dates, expected, 'date range is wrong')

    def test_temperature_convert(self):
        data = [(49, 9.44), (50, 10.00), (51, 10.56)]
        for t, expected in data:
            with self.subTest(i=t):
                self.assertEqual(crawler.fahrenheit_to_celsius(t), expected)

    def test_url_compose(self):
        excepted = 'https://api.weather.com/v1/location/ZLXY:9:CN/observations/historical.json?apiKey=get_your_api_key&units=e&startDate=20211101&endDate=20211130'
        self.assertEqual(crawler.compose_url(
            (20211101, 20211130)), excepted, "url compose failed")

    def test_convert_data_to_expected_shape(self):
        expected = json.loads(
            '{"temp": 50, "date_time": "2021-11-01 00:00:00", "temp_centigrade": 10.0}')
        input_obj = json.loads('{"temp": 50, "valid_time_gmt": 1635696000}')
        result = crawler.convert_data_to_expected_shape(input_obj)
        self.assertEqual(result, expected)

    def test_year_range(self):
        data = [(2021, 0, [2021]),
                (2021, 1, [2021, 2022]),
                (2021, 2, [2021, 2022, 2023])
                ]
        for start, step, expected in data:
            with self.subTest():
                actual = crawler.get_years_range(start, step)
                self.assertEqual(actual, expected)


if __name__ == "__main__":
    unittest.main()
