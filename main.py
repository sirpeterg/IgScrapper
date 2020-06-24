# Github user: sirpeterg
# date: 2020-06-23
# version 0.2
# major changes since 0.1: using the Instaloader module

##################################
#HIGH LEVEL
##################################
#while not EndConditionReached:

    # 0) check the status of the DB, and make a decision what to do, based on the status
        # if enough ulrs are in DB that are not downloaded, grab some of them
        # else, get new post urls into DB (using UserList.txt, a file with names of users to scrap)

    # 1) get list of posts from random user, from the DB

    # 2.1) download the image

    # 2.2) if image was saved get the metadata (likes etc, statistics of user) and write to DB

    # Do pause

##################################



import instaloader
from instaloader import Post, Profile
from selenium import webdriver
import IGDBactions
import sqlite3
import time
from random import randint, random
from instaloader import Post, Profile
import datetime
import os

class WebDriver:
    def __init__(self, driver):
        self.driver = driver

    def __enter__(self):
        return self.driver

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.driver.quit()

def main():
    home_path = '/Users/Peterg/code/IgScrapper'
    picture_save_flag = False
    max_runtime_minutes = 454
    start_scrapping = datetime.datetime.now()
    driverchoice = ['Chrome', 'Firefox'][1]
    if driverchoice == 'Chrome':
        webdriver_path = home_path +'/chromedriver' # chrome driver
        browser = 'Chrome'
    elif driverchoice == 'Firefox':
        webdriver_path = home_path + '/geckodriver' # chrome driver
        #webdriver_path = '/Users/Peterg/code/IgScrapper/geckodriver' # firefox driver
        browser = 'Firefox'
    else:
        print('Unsupported driver')
    while True:
        duration_run = datetime.datetime.now() - start_scrapping
        duration_run_minutes = round(duration_run.total_seconds() / 60, 2)
        EndconditionReached = duration_run_minutes > max_runtime_minutes
        if EndconditionReached:
            print("SCRAPPING RUN IS DONE, END CONDITION REACHED")
            break
        ###########################################
        print('')
        print("_____ MODULE 0__________")
        print("CHECK STATUS OF DB (make a decision if new picture urls are required)")
        print("_____ MODULE 0__________")
        print("|")

        # establish a DB connection

        connection = sqlite3.connect(home_path + '/Database_img/IGdata.db')
        cursor = connection.cursor()

        # create database structure if empty
        IGDBactions.create_photo_db_entry(connection, cursor)

        # check if there are entries
        minimum_num_links_for_scrapping = 10
        enough_picture_links_available = False
        print("|    DATABASE STATUS - before")
        numDbEntries, \
        numImgMetadataNotDownloaded, \
        numImgNotDownloaded = IGDBactions.getDBStatus(connection, cursor)

        if numImgNotDownloaded > minimum_num_links_for_scrapping:
            print('|    Enough picture urls in DB')
            enough_picture_links_available = True
        else:
            print('|    Need more picture urls in DB')
            enough_picture_links_available = False
        print("__")
        print("")
        ###########################################
        print("")
        print("_____ MODULE 1__________")
        print("GET PHOTO URLS")
        print("_____ MODULE 1__________")
        print("|")
        while not enough_picture_links_available:
            print("|    updating DB, adding more post urls")
            with eval('WebDriver(webdriver.' + browser + '(executable_path=webdriver_path))') as driver:
                # go to a random IG user (from UserList.txt file), scrap a handful post_urls, and write into DB
                enough_picture_links_available = get_new_post_urls_to_DB(driver, cursor, connection,
                                      enough_picture_links_available,
                                      minimum_num_links_for_scrapping,
                                      home_path)
        # if enough post_urls are in DB, then take the post_urls from the DB
        post_urls, photographer_names = get_list_of_post_urls(cursor)
        post_url, photographer_name = decidewhichposturl(post_urls, photographer_names)  # picking a random url
        #post_url = 'https://www.instagram.com/p/CAnp1P3D7D3/'
        #photographer_name = 'nathanielwise'

        print('|    random url: ', post_url, 'photographer: ', photographer_name)
        print("__")
        print("")
        ####################
        print("_____ MODULE 2.1__________")
        print("VISIT RANDOM PHOTO URL (scrap image)")
        print("_____ MODULE 2.1__________")
        print("|")
        photographer_name = photographer_name.rstrip() # getting rid of newlines and whitespaces
        shortcode = post_url.split('/')[-2]
        folderpath = 'Database_img/' + photographer_name
        L = instaloader.Instaloader(filename_pattern='{shortcode}',
                                    dirname_pattern= folderpath,
                                    download_videos=False,
                                    download_video_thumbnails=False,
                                    compress_json = False,
                                    save_metadata = False,
                                    download_comments = False,
                                    post_metadata_txt_pattern = '')
        profile = Profile.from_username(L.context, photographer_name)
        post = Post.from_shortcode(L.context, shortcode)
        try:
            picture_save_flag = L.download_post(post, target='DB' + profile.username, )
            #print('DONE, image scrapped (or is video and was not saved, see next message)')
            #print('tentative picture_save_flag: ', picture_save_flag)
        except:
            picture_save_flag = False
            #print('image could not be saved')
        #if picture_save_flag == True:
        Remove_trailing_mulitimages(shortcode, photographer_name, home_path) # I only want to save one image per post

        is_in_DB = is_jpg_in_DB(home_path, photographer_name, shortcode)
        if not is_in_DB:
            picture_save_flag = False # some multi-videos went under the radar. Hence, I check if the jpg is there
            # if not, I flag that nothing was saved
            print("|    jpg could not be saved!")
        else:
            print("|    DONE, jpg was saved!")
            picture_save_flag = True

        if post.is_video == True:
            print('|    post could not be saved, it was a video')
        #else:
        #    print('image could be saved, is no video')
        # write into DB that the image was saved
        if picture_save_flag == True:
            # identify the DB ID of the post url
            cursor.execute("SELECT photo_id FROM photo WHERE photo_url = ? ", (post_url,))
            photo_id = cursor.fetchall()[0][0]
            # write metadata into DB
            #print("Using following ID: ", photo_id)
            cursor.execute("UPDATE photo SET is_downloaded = ? WHERE photo_id = ?;", ('True', photo_id))
            print("|    Updated the saving event to the database")
            connection.commit()

        print("__")
        print("")
        ####################
        print("_____ MODULE 2.2__________")
        print("VISIT RANDOM PHOTO URL (scrap metadata)")
        print("_____ MODULE 2.2__________")
        print("|")
        if picture_save_flag == True:
            metadata = get_metadata(profile, post)
            writeMetadataToDB(post_url, cursor, connection, metadata)
            print('|    DONE, metadata scrapped')
            print("|    DATABASE STATUS - after")
            IGDBactions.getDBStatus(connection, cursor)
        else:
            print('|    No metadata scrapped, since no image was saved')
        #print("is video?: ", post.is_video)
        if post.is_video == True:
            # remove the entry from database
            print("|    is video?: ", post.is_video)
            print('|    removing db entry since post is video')
            cursor.execute("DELETE FROM photo WHERE photo_url = (?);", (post_url,))
        print("__")
        print("")
        ####################
        # do pause

        print("_____ MODULE 3__________")
        print("Ending Cycle")
        print("_____ MODULE 3__________")
        print("|")
        print("|    Current time:", datetime.datetime.now())
        pause('XL')
        if random() < 0.12:
            pause('L')
        print("_")
        print("")
        ####################
    print("No more Jobs, I am done \n")
    print("Current time:", datetime.datetime.now())
    print("### DATABASE STATUS AT END ######")
    IGDBactions.getDBStatus(connection, cursor)

####################

def get_metadata(profile, post):
    data_profile = profile._asdict() # accessing the metadata dict from the profile structure
    data_post= post._asdict() # accessing the metadata dict from the post structure
    metadata = {}
    # get likes
    metadata['likes'] = post.likes
    # get age
    timestamp = str(data_post['taken_at_timestamp'])
    timetaken = datetime.datetime.fromtimestamp(int(timestamp)).strftime('%Y-%m-%d %H:%M:%S')
    datetimeFormat = '%Y-%m-%d %H:%M:%S'
    postdate = datetime.datetime.strptime(timetaken, datetimeFormat)
    time_now = datetime.datetime.now()
    dt = time_now - postdate
    TimeDifferenceInHours = dt.total_seconds() / 3600.0
    TimeDifferenceInDays = TimeDifferenceInHours / 24.0
    TimeDifferenceInDays = round(TimeDifferenceInDays, 2)
    metadata['age'] = TimeDifferenceInDays
    # get date now
    metadata['downloaded'] = str(datetime.datetime.now())
    # get image descriptions
    try:
        metadata['IG_category'] = data_post['edge_sidecar_to_children']['edges'][0]['node']['accessibility_caption'].split('Image may contain:')[1].split("\n")[0]
    except:
        metadata['IG_category'] = ''
    # get hashtags
    hashtags_original = post.caption_hashtags # reformating into one string with '#' in front
    hashtags = []
    for tags in hashtags_original:
        hashtags.append('#' + tags)
    hashtags_str = str(hashtags).replace(",", "").replace("'", "").replace("[", "").replace("]", "")
    metadata['hashtags'] = hashtags_str
    metadata['username'] = data_post['owner']['username']
    metadata['followers'] = data_post['owner']['edge_followed_by']['count']
    metadata['following'] = data_profile['edge_follow']['count']
    return metadata


def get_new_post_urls_to_DB(driver, cursor, connection,
                        enough_picture_links_available,
                        minimum_num_links_for_scrapping,
                        home_path):
    while not enough_picture_links_available:
        cursor.execute("SELECT * FROM photo ")
        results = cursor.fetchall()
        numberDbEntries = len(results)
        NumberImagesNotDownloaded = IGDBactions.getNumberNotDownloaded(connection, cursor)
        print('|    Number of picture links: ', numberDbEntries, ' and Number of pictures not downloaded: ',
              NumberImagesNotDownloaded)
        if NumberImagesNotDownloaded < minimum_num_links_for_scrapping:
            print('|    Getting new picture urls')
            get_post_url_to_DB(driver, minimum_num_links_for_scrapping, connection, cursor, home_path)
        else:
            print('|    Enough picture urls in DB')
            enough_picture_links_available = True
    print('|    DB updated with new post URLs')
    return enough_picture_links_available


def get_list_of_post_urls(cursor):
    cursor.execute("SELECT photo_url FROM photo WHERE is_downloaded = 'False'")
    post_urls = cursor.fetchall()
    cursor.execute("SELECT photographer_name FROM photo WHERE is_downloaded = 'False'")
    photographer_names = cursor.fetchall()
    return post_urls, photographer_names


def get_post_url_to_DB(driver, n, connection, cursor, home_path):
    with open(home_path + '/UserList.txt', 'r') as opened_file:
        allusers = opened_file.readlines()
    total_names = len(allusers)
    # will throw the dice which user to pick
    random_no = randint(0, total_names - 1)
    print('|    Total users in txt file: ', total_names)
    user_tocheck = allusers[random_no].replace('/', '')
    user_tocheck = user_tocheck[:-1] # getting rid of the trailing 'ENTER'
    print('|    picking entry number : ', random_no, ' User name: ', user_tocheck)
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
            pause('M')

        pause('L')
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


def decidewhichposturl(post_urls, photographer_names):
    number_ulrs = len(post_urls)
    randomnum = randint(0,number_ulrs-1)
    post_url = post_urls[randomnum]
    photographer_name = photographer_names[randomnum]
    return post_url[0], photographer_name[0]


def writeMetadataToDB(post_url, cursor, connection, metadata):
    cursor.execute("SELECT photo_id FROM photo WHERE photo_url = ? ", (post_url,))
    photo_id = cursor.fetchall()[0][0]
    #print("Using following ID: ", photo_id)
    #print("metadata is:", metadata)
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
    cursor.execute("UPDATE photo SET followers = ? WHERE photo_id = ?;", (str(metadata['followers']), photo_id))
    connection.commit()
    cursor.execute("UPDATE photo SET following = ? WHERE photo_id = ?;", (str(metadata['following']), photo_id))
    connection.commit()


def Remove_trailing_mulitimages(shortcode, photographer_name, home_path):
    path = home_path +'/Database_img/' + photographer_name
    files = []
    for i in os.listdir(path):
        if os.path.isfile(os.path.join(path, i)) and shortcode in i:
            files.append(i)
    #print("these are the logged files: ", files)
    if files:
        os.rename(path + '/' + files[0], path + '/' + shortcode + '.jpg')  # rename the first image to its shortcode name.
        # This is neutral for normal, non-multiimages, does not effectively change its name
        if len(files) >= 2: # multiimage
            for i in range(1, len(files)):
                os.remove(path + '/' + files[i]) # delete all but the first multiimage

def is_jpg_in_DB(home_path, photographer_name, shortcode):
    path = home_path + '/Database_img/' + photographer_name
    is_in_DB = os.path.isfile(path + '/' + shortcode + '.jpg')
    return is_in_DB

def pause(size):
    # weird numbers intentional, to not look too much like a computer
    if size == 'XS':
        pauselength = 5.1 * (random() + 0.05) # between 0.5 sec and 5 sec
    elif size == 'S':
        pauselength = 15.4 * (random() + 0.1) # between 1.5 sec and 15 sec
    elif size == 'M':
        pauselength = 50.7 * (random() + 0.1) # between 5 sec and 1 min
    elif size == 'L':
        pauselength = 141.3 * (random() + 0.1) # between 0.5 and 2.84 min
    elif size == 'XL':
         pauselength = 141.3 * (random() + 0.21) + 272 # between 5.02 and 7.38 min
    elif size == 'XXL':
        pauselength = 3130 * (random() + 0.05) + 412 # between 9.475 and 61.6 min

    print('|    Pausing for: ', round(pauselength / 60.0, 1), ' minutes')
    time.sleep(pauselength)



if __name__ == '__main__': main()