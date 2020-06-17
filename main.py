import sqlite3
import sys
import time
from selenium import webdriver
from datetime import datetime, timedelta
sys.path.append('/Users/Peterg/Documents/Python/InstaBot')
sys.path.append('/Users/Peterg/Documents/Python/IG_data')
import IGactions
import IGDBactions
import requests
import random
from random import randint


class WebDriver:
    def __init__(self, driver):
        self.driver = driver

    def __enter__(self):
        return self.driver

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.driver.quit()

# # stuff for a headless Chrome browser and proxy
# options = Options()
# options.add_argument('--headless')
# options.add_argument('--disable-gpu')  # Last I checked this was necessary.
# options.add_argument('--no-sandbox')


##################################
#HIGH LEVEL
##################################
# 0) check the status of the DB, and make a decision what to do, based on the status

# 1) get list of posts from random user (from text file)

#while not EndConditionReached:
    # make random decision, do 2.1 or 2.2

    # 2.1) go to image (random), get the metadata (likes etc, statistics of user) and

    # 2.2) download the image

    # Do pause
##################################



def main():

    driverchoice  = ['Chrome', 'Firefox'][1]
    if driverchoice == 'Chrome':
        webdriver_path = '/Users/Peterg/Documents/Python/InstaBot/chromedriver' # chrome driver
        browser = 'Chrome'
    elif driverchoice == 'Firefox':
        webdriver_path = '/Users/Peterg/Documents/Python/InstaBot/geckodriver' # firefox driver
        browser = 'Firefox'
    else:
        print('Unsupported driver')

    ###########################################
    print("_____ MODULE 0__________")
    print("CHECK STATUS OF DB (make a decision if new picture urls are required)")
    print("_____ MODULE 0__________")
    print("")
    # check if you can open and close the DB
    connection = sqlite3.connect('/Users/Peterg/Documents/Python/IG_scrapper_V2/Database_img/IGdata.db')
    connection.close()
    # establish a DB connection
    connection = sqlite3.connect('/Users/Peterg/Documents/Python/IG_scrapper_V2/Database_img/IGdata.db')
    cursor = connection.cursor()

    # create database structure if empty
    IGDBactions.create_photo_db_entry(connection, cursor)

    # check if there are entries
    minimum_num_links_for_scrapping = 8
    enough_picture_links_available = False
    print("### DATABASE STATUS AT START ######")
    numDbEntries, \
    numImgMetadataNotDownloaded, \
    numImgNotDownloaded = IGDBactions.getDBStatus(connection, cursor)

    if numImgNotDownloaded > minimum_num_links_for_scrapping:
        print('Enough picture urls in DB')
        enough_picture_links_available = True
    else:
        print('Need more picture urls in DB')
        enough_picture_links_available = False

    ###########################################
    print("")
    print("_____ MODULE 1__________")
    print("GET PHOTO URLS")
    print("_____ MODULE 1__________")
    print("")

    ## random choice : get picture metadata or get picture
    NextAction = random.choice(['scrap_metadata', 'scrap_picture'])
    #NextAction = 'scrap_metadata'
    #NextAction = 'scrap_picture'

    # get list of urls where (list length is not fixed size, but typically not smaller than n = 8
    # a) metadata is missing (see nextaction)
    # or b) the picture is not downloaded (see nextaction)
    with eval('WebDriver(webdriver.' + browser + '(executable_path=webdriver_path))') as driver:
        post_urls, photographer_names = get_list_of_post_urls(driver, cursor, connection,
                                                                      enough_picture_links_available, NextAction)
    # if enough post_urls are in DB, then take the post_urls from the DB
    # else go to a random IG user (from user.txt file, and scrap a handful of post_urls

    post_url, photographer_name = decidewhichposturl(post_urls, photographer_names) # picking a random url
    print('random url: ', post_url, 'photographer: ', photographer_name)

    ### FOR DEBUGGING ONLY, REMOVE BELOW
    print('this many urls available: ', len(post_urls))
    print('urls: ', post_urls)
    print('photographers: ', photographer_names)
    for uurl in post_urls:
        cursor.execute("SELECT photo_id FROM photo WHERE photo_url = (?)", (uurl))
        iid = cursor.fetchall()
        print('pic id:', iid)
    NextAction = 'takeabreak'
    ### FOR DEBUGGING ONLY, REMOVE ABOVE


    ###########################################
    if NextAction == 'scrap_metadata':
        print("_____ MODULE 2.1__________")
        print("VISIT RANDOM PHOTO URL (scrap metadata)")
        print("_____ MODULE 2.1__________")
        print("")

        ## random choice : get picture metadata before or after get photographer metadata (two different url lists need to be processed)
        usermetadata_before_picturemetadata = random.choice([True, False])

        if usermetadata_before_picturemetadata == True:
            # get metadata: Photographer -> go to user page -> get post number  ->get follower  ->number get followees number
            with eval('WebDriver(webdriver.' + browser + '(executable_path=webdriver_path))') as driver:
                print('getting photographer data')
                url = "https://www.instagram.com/" + photographer_name + "/"
                driver.get(url)
                posts_no, followee_no, follower_no = IGactions.getUserFollowerNumber(driver)
                IGactions.pause('L')

        # get metadata: Picture -> go to image ->get likes ->get age ->get date now ->get image descriptions ->get hashtags
        with eval('WebDriver(webdriver.' + browser + '(executable_path=webdriver_path))') as driver:
            print('getting metadata')
            metadata = IGactions.get_metadata(driver, post_url)
            IGactions.pause('L')

        if usermetadata_before_picturemetadata == False:
            # get metadata: Photographer -> go to user page -> get post number  ->get follower  ->number get followees number
            with eval('WebDriver(webdriver.' + browser + '(executable_path=webdriver_path))') as driver:
                print('getting photographer data')
                url = "https://www.instagram.com/" + photographer_name + "/"
                driver.get(url)
                posts_no, followee_no, follower_no = IGactions.getUserFollowerNumber(driver)
                IGactions.pause('L')


        # identify the DB ID of the post url
        cursor.execute("SELECT photo_id FROM photo WHERE photo_url = ? ", (post_url,))
        photo_id = cursor.fetchall()[0][0]
        print("Using following ID: ", photo_id)
        print("metadata is:", metadata)
        # write metadata into DB
        cursor.execute("UPDATE photo SET likes = ? WHERE photo_id = ?;", (str(metadata['likes']), photo_id))
        connection.commit()
        cursor.execute("UPDATE photo SET age = ? WHERE photo_id = ?;", (str(metadata['age']), photo_id))
        connection.commit()
        cursor.execute("UPDATE photo SET downloaded = ? WHERE photo_id = ?;", (str(metadata['downloaded']), photo_id))
        connection.commit()
        cursor.execute("UPDATE photo SET IG_category = ? WHERE photo_id = ?;", (str(metadata['IG_category']), photo_id))
        connection.commit()
        cursor.execute("UPDATE photo SET hashtags = ? WHERE photo_id = ?;", (str(metadata['hashtags']), photo_id))
        connection.commit()
        cursor.execute("UPDATE photo SET followers = ? WHERE photo_id = ?;", (str(follower_no), photo_id))
        connection.commit()
        cursor.execute("UPDATE photo SET following = ? WHERE photo_id = ?;", (str(followee_no), photo_id))
        connection.commit()

###########################################
    elif NextAction == 'scrap_picture':
        print("_____ MODULE 2.2__________")
        print("VISIT RANDOM PHOTO URL (scrap image)")
        print("_____ MODULE 2.2__________")
        print("")
        # go to image -> download image
        with eval('WebDriver(webdriver.' + browser + '(executable_path=webdriver_path))') as driver:
            img_save_flag =  IGactions.insta_url_to_img(post_url, driver, photographer_name, [])

        # write into DB that the image was saved
        if  img_save_flag == True:
            # identify the DB ID of the post url
            cursor.execute("SELECT photo_id FROM photo WHERE photo_url = ? ", (post_url,))
            photo_id = cursor.fetchall()[0][0]
            # write metadata into DB
            print("Using following ID: ", photo_id)
            cursor.execute("UPDATE photo SET is_downloaded = ? WHERE photo_id = ?;", ('True', photo_id))
            print("Updated the saving event to the database")
            connection.commit()


    print("No more Jobs, I am done \n")
    print("Current time:", datetime.now())
    print("### DATABASE STATUS AT END ######")
    IGDBactions.getDBStatus(connection, cursor)




#######################################





def get_list_of_post_urls(driver, cursor, connection, enough_picture_links_available, Next_Action, minimum_num_links_for_scrapping):
    if enough_picture_links_available:
        pass # the list of urls is read from the DB at the end of the function
    else: # download more and write to DB
        while not enough_picture_links_available:
            cursor.execute("SELECT * FROM photo ")
            results = cursor.fetchall()
            numberDbEntries = len(results)
            NumberImagesNotDownloaded = IGDBactions.getNumberNotDownloaded(connection, cursor)
            NumberImagesMetadataNotDownloaded = IGDBactions.getNumberMetadataNotDownloaded(connection, cursor)
            print('Number of picture links: ', numberDbEntries, ' and Number of pictures not downloaded: ', NumberImagesNotDownloaded)
            if NumberImagesNotDownloaded < minimum_num_links_for_scrapping or NumberImagesMetadataNotDownloaded < minimum_num_links_for_scrapping:
                print('Getting new picture urls')
                get_post_url_to_DB(driver, minimum_num_links_for_scrapping, connection, cursor)
            else:
                print('Enough picture urls in DB')
                enough_picture_links_available = True
        print('Enough links to IG pictures available')
    if Next_Action == 'scrap_picture': # get all urls (along with the associated potographer name) where image is not downloaded
        cursor.execute("SELECT photo_url FROM photo WHERE is_downloaded = 'False'")
        post_urls = cursor.fetchall()
        cursor.execute("SELECT photographer_name FROM photo WHERE is_downloaded = 'False'")
        photographer = cursor.fetchall()
    elif Next_Action == 'scrap_metadata': # get all urls (along with the associated potographer name) where metadata is not downloaded
        cursor.execute("SELECT photo_url FROM photo WHERE likes = 'None'")
        post_urls = cursor.fetchall()
        cursor.execute("SELECT photographer_name FROM photo WHERE likes = 'None'")
        photographer_names = cursor.fetchall()

    return post_urls, photographer_names

def decidewhichposturl(post_urls, photographer_names):
    number_ulrs = len(post_urls)
    randomnum = randint(0,number_ulrs-1)
    post_url = post_urls[randomnum]
    photographer_name = photographer_names[randomnum]
    return post_url[0], photographer_name[0]


def get_post_url_to_DB(driver, n, connection, cursor):
    with open('/Users/Peterg/Documents/Python/IG_data/UserList.txt', 'r') as opened_file:
        allusers = opened_file.readlines()
    total_names = len(allusers)
    # will throw the dice which user to pick
    random_no = randint(0, total_names - 1)
    print('Total users in txt file: ', total_names)
    user_tocheck = allusers[random_no].replace('/', '')
    print('picking entry number : ', random_no, ' User name: ', user_tocheck)
    url = "https://www.instagram.com/" + user_tocheck + "/"
    driver.get(url)
    post = 'https://www.instagram.com/p/'
    post_links = []
    number_ignored_duplicates = 0
    while len(post_links) < n:
        links = [a.get_attribute('href') for a in driver.find_elements_by_tag_name('a')]
        for link in links:
            # check if link is already in database:
            cursor.execute("SELECT photo_url FROM photo WHERE photo_url = (?);", (link,))
            similar_link = cursor.fetchall()
            if similar_link:
                is_duplicate = True
            else:
                is_duplicate = False
            if not is_duplicate: # the link is not in the DB already
                if post in link and link not in post_links: # is valid link and has not been added to the list in this loop
                    post_links.append(link)
            else:
                number_ignored_duplicates = number_ignored_duplicates + 1
                #print('number_ignored_duplicates: ', number_ignored_duplicates)
        if n > 12 or number_ignored_duplicates > 6:
            scroll_down = "window.scrollTo(0, document.body.scrollHeight);"
            driver.execute_script(scroll_down)
            IGactions.pause('L')
            time.sleep(randint(1,7))

        IGactions.pause('L')
    if len(post_links) > n: # crop to desired length
        post_links = post_links[0:n]
    # Duplicates should have not been added. As extra safety, I remove potential duplicates (redundant, can probably be removed)
    post_links = IGDBactions.removeIfAlreadyInDatabase(post_links, cursor)


    for post in post_links:
        post_name = post.split('/')[-2]
        IGDBactions.insertPhotoInDB(connection, cursor, post_name, post,
                                   None, None, None, None, None, user_tocheck, None,
                                   None)  # only ID and post and photographername
    return post_links, user_tocheck


if __name__ == '__main__': main()
