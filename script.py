"""
Scrapes a headline from The Daily Pennsylvanian website and saves it to a 
JSON file that tracks headlines over time.
"""

import os
import sys

import daily_event_monitor

import bs4
import requests
import loguru


def scrape_data_point():
    """
    Scrapes the main headline from The Daily Pennsylvanian home page.

    Returns:
        str: The headline text if found, otherwise an empty string.
    """
    req = requests.get("https://www.thedp.com")
    loguru.logger.info(f"Request URL: {req.url}")
    loguru.logger.info(f"Request status code: {req.status_code}")

    if req.ok:
        soup = bs4.BeautifulSoup(req.text, "html.parser")
        target_element = soup.find("a", class_="frontpage-link")
        data_point = "" if target_element is None else target_element.text
        loguru.logger.info(f"Data point: {data_point}")
        return data_point
    
def scrape_featured_headlines() -> list:
    """
    Scrapes the (3) featured headlines from The Daily Pennsylvanian home page.
    
    Returns:
        list[str]: A list of headlines if found, otherwise an empty list
    """
    
    req = requests.get("https://www.thedp.com")
    loguru.logger.info(f"Request URL: {req.url}")
    loguru.logger.info(f"Request status code: {req.status_code}")
    
    if req.ok:
        soup = bs4.BeautifulSoup(req.text, "html.parser")
        target_divs = soup.findAll("div", class_="special-edition")
        target_a_items = [item.find("a", class_="frontpage-link standard-link") for item in target_divs]
        
        formatted_titles = [str(a.text.strip()) for a in target_a_items]
        return formatted_titles
    else:
        return []

def scrape_most_recent_headlines() -> list:
    """
    Scrapes the (4-5) most reacent headlines from The Daily Pennsylvanian home page (as featured on the right-sidebar).
    
    Returns:
        list[str]: A list of headlines if found, otherwise an empty list
    """
    
    req = requests.get("https://www.thedp.com")
    loguru.logger.info(f"Request URL: {req.url}")
    loguru.logger.info(f"Request status code: {req.status_code}")
    
    if req.ok:
        soup = bs4.BeautifulSoup(req.text, "html.parser")
        target_div_items = soup.findAll("div", class_="story sidebar-story")
        formatted_titles = [str(a.text.strip()) for a in target_div_items]
        
        return formatted_titles
    else:
        return []

def scrape_social_media_links() -> dict:
    """
    Scrapes The Daily Pennsylvanian's Facebook, Instagram and Twitter social media links
    
    Returns:
    dict[str]: A simple key value dictionary, where values are strings if links are found, empty dictionary otherwise
    """
    
    req = requests.get("https://www.thedp.com")
    loguru.logger.info(f"Request URL: {req.url}")
    loguru.logger.info(f"Request status code: {req.status_code}")
    
    
    if req.ok:
        soup = bs4.BeautifulSoup(req.text, "html.parser")
        target_ul = soup.find("ul", class_="social-icons")
        target_li = target_ul.findAll("li")
    
        links = []
    
        for li in target_li:
            target_a_ele = li.find("a")
            
            href = target_a_ele.get("href")
            if href:   
                links.append(target_a_ele.get("href"))
        
        formatted_output = {}
        for link in links:
            if "facebook.com" in link:   
                formatted_output["facebook"] = link
            elif "twitter.com" in link:
                formatted_output["twitter"] = link
            elif "instagram.com" in link:
                formatted_output["instagram"] = link
        
        return formatted_output 
    else:
        return {}


if __name__ == "__main__":

    # Setup logger to track runtime
    loguru.logger.add("scrape.log", rotation="1 day")

    # Create data dir if needed
    loguru.logger.info("Creating data directory if it does not exist")
    try:
        os.makedirs("data", exist_ok=True)
    except Exception as e:
        loguru.logger.error(f"Failed to create data directory: {e}")
        sys.exit(1)

    # Load daily event monitor
    loguru.logger.info("Loading daily event monitor")
    dem = daily_event_monitor.DailyEventMonitor(
        "data/daily_pennsylvanian_headlines.json"
    )

    # Run scrape
    loguru.logger.info("Starting scrape")
    try:
        data_point = scrape_data_point()
        
        feat_headlines = scrape_featured_headlines()
        most_recent = scrape_most_recent_headlines()
        social_media = scrape_social_media_links()
    except Exception as e:
        loguru.logger.error(f"Issue when trying to scrape some data point: {e}")
        data_point = None
        
        feat_headlines = None
        most_recent = None
        social_media = None

    # Save data
    if data_point is not None:
        dem.add_today(data_point)
        dem.save()
        loguru.logger.info("Saved daily event monitor")
        
    my_out = {}
        
    if feat_headlines is not None:
        my_out["featured_headlines"] = feat_headlines
        loguru.logger.info("Inserted featured headlines event monitor")
    if most_recent is not None:
        my_out["recent_headlines"] = most_recent
        loguru.logger.info("Inserted most recent headlines event monitor")
    if social_media is not None:
        my_out["social_links"] = social_media
        loguru.logger.info("Inserted social media links event monitor")
        
    dem.add_today(my_out)
    dem.save()
    loguru.logger.info("Saved all scraped data")

    def print_tree(directory, ignore_dirs=[".git", "__pycache__"]):
        loguru.logger.info(f"Printing tree of files/dirs at {directory}")
        for root, dirs, files in os.walk(directory):
            dirs[:] = [d for d in dirs if d not in ignore_dirs]
            level = root.replace(directory, "").count(os.sep)
            indent = " " * 4 * (level)
            loguru.logger.info(f"{indent}+--{os.path.basename(root)}/")
            sub_indent = " " * 4 * (level + 1)
            for file in files:
                loguru.logger.info(f"{sub_indent}+--{file}")

    print_tree(os.getcwd())

    loguru.logger.info("Printing contents of data file {}".format(dem.file_path))
    with open(dem.file_path, "r") as f:
        loguru.logger.info(f.read())

    # Finish
    loguru.logger.info("Scrape complete")
    loguru.logger.info("Exiting")
