import slack
import time
import logging
import sys
import traceback
import json
import os
import importlib


from craigslist import CraigslistHousing
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, DateTime, Float, Boolean
from sqlalchemy.orm import sessionmaker
from dateutil.parser import parse

# logging
logging.basicConfig(level=logging.INFO)

# slack
SLACK_API_TOKEN = os.environ.get("SLACK_API_TOKEN")
slack_client = slack.WebClient(token=SLACK_API_TOKEN)

# configs
# this can instead be read as file instead of module
CONFIG_NAME = os.environ.get("CONFIG_NAME")
CONFIG = importlib.import_module(f"configs.{CONFIG_NAME}")

# Listing class
Base = declarative_base()


class Listing(Base):
    """
    A table to store data on craigslist listings.
    """

    __tablename__ = "listings"

    id = Column(Integer, primary_key=True)
    cl_id = Column(Integer, unique=True)
    cl_site = Column(String)
    cl_area = Column(String)
    cl_category = Column(String)
    url = Column(String, unique=True)
    name = Column(String)
    price = Column(Float)
    area = Column(Integer)
    bedrooms = Column(Integer)
    location = Column(String)
    geotag = Column(String)
    lat = Column(Float)
    lon = Column(Float)
    has_image = Column(Boolean)
    has_map = Column(Boolean)
    created = Column(DateTime)

    # TODO: implement this
    def __repr__(self):
        pass

# db
engine = create_engine(CONFIG.DB, echo=False)
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()


def post_listing_to_slack(listing):
    """
    Posts the listing to slack.
    :param listing: A record of the listing.
    """
    logging.info(f"{time.ctime()}: Posting cl_id={listing.cl_id} to slack")
    description = f"{listing.name} | {listing.price} | {listing.area} | {listing.url}"
    response = slack_client.chat_postMessage(
        channel=CONFIG.SLACK_CHANNEL, text=description, icon_emoji=":robot_face:"
    )
    return response


def to_numeric(s, converter):
    try:
        v = converter(s)
    except ValueError:
        v = None
    return v


def scrape_craigslist_housing():
    listings = []
    craigslist_housing = CraigslistHousing(
        site=CONFIG.SITE,
        area=CONFIG.AREA,
        category=CONFIG.CATEGORY,
        filters=CONFIG.FILTERS,
    )

    results = craigslist_housing.get_results(sort_by="newest", geotagged=True, limit=20)

    for result in results:
        logging.info(f'{time.ctime()}: Processing cl_id={result["id"]}')
        listing = session.query(Listing).filter_by(cl_id=result["id"]).first()

        if listing:
            logging.info(f"{time.ctime()}: cl_id={result['id']} Already in db")
            continue

        lat, lon = result.get("geotag", (None, None))

        listing = Listing(
            cl_id=result["id"],
            cl_site=CONFIG.SITE,
            cl_area=CONFIG.AREA,
            cl_category=CONFIG.CATEGORY,
            url=result["url"],
            name=result["name"],
            price=to_numeric(result.get("price", "").replace("$", ""), float),
            area=to_numeric(str(result.get("area", "")).replace("ft2", ""), float),
            bedrooms=result["bedrooms"],
            location=result["where"],
            geotag=f"({lat},{lon})",
            lat=to_numeric(lat, float),
            lon=to_numeric(lon, float),
            has_image=result["has_image"],
            has_map=result["has_map"],
            created=parse(result["datetime"]),
        )

        logging.info(f"{time.ctime()}: Saving cl_id={listing.cl_id}")
        session.add(listing)
        session.commit()
        listings.append(listing)
    return listings


def main():
    while True:
        logging.info(f"{time.ctime()}: Starting scrape cycle")
        try:
            listings = scrape_craigslist_housing()

            if listings:
                logging.info(f"{time.ctime()}: Posting listings to slack")
            for listing in listings:
                post_listing_to_slack(listing)

        except KeyboardInterrupt:
            logging.info(f"{time.ctime()}: Exiting....")
            sys.exit(1)
        except Exception:
            logging.error(f"{time.ctime()}: Error with scraping: {sys.exc_info()}")
            traceback.print_exc()
        else:
            logging.info(
                f"{time.ctime()}: Successfully finished scraping cycle. Sleeping for {CONFIG.SLEEP_INTERVAL}."
            )
        time.sleep(CONFIG.SLEEP_INTERVAL)


if __name__ == "__main__":
    main()
