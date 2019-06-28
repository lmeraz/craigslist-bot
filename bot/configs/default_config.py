SLACK_CHANNEL = "#housing"
SLEEP_INTERVAL = 20 * 60
SITE = "sfbay"
AREA = "sfc"
CATEGORY = "apa"
FILTERS = {
    "min_price": 1600,
    "max_price": 2400,
    "posted_today": True,
    "bundle_duplicates": True,
    "zip_code": 94103,
    "search_distance": 2.2,
    "min_bedrooms": 0,
    "min_bathrooms": 1,
}
DB = 'sqlite:///db/listings.db'