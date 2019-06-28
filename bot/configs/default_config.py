# settings file
# to do: this may be better as json or different format only reason is because 
SLACK_CHANNEL = "#housing"
SLEEP_INTERVAL = 20 * 60 # in seconds
SITE = "sfbay" # subdomain
AREA = "sfc" # the city
CATEGORY = "apa" # apartments
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