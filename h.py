from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time

def play_song_with_selenium(song_name):
    driver = webdriver.Chrome()
    # Search for the song on YouTube
    driver.get("https://www.youtube.com")
    search_box = driver.find_element_by_name("search_query")
    search_box.send_keys(song_name)
    search_box.send_keys(Keys.RETURN)

    # Wait for search results and click the first video
    time.sleep(3)
    videos = driver.find_elements_by_id("video-title")
    if videos:
        videos[0].click()
        time.sleep(2)


play_song_with_selenium("Dil")