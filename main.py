# Github user: sirpeterg
# date: 2020-06-23
# version 0.3
# changes: Switched from
# functional to object oriented design

##################################
#HIGH LEVEL
##################################
#while not EndConditionReached:

    # 0) check the status of the DB, and make a decision what to do, based on the status
        # if enough ulrs are in DB that are not downloaded, grab some of them to the DB
        # else, get new post urls into DB (using UserList.txt, a file with names of users to scrap)

    # 1) get list of posts from random user, from the DB

    # 2.1) download the image

    # 2.2) if image was saved get the metadata (likes etc, statistics of user) and write to DB

    # Do pause

##################################

import instaloader
from selenium import webdriver
import sqlite3
import time
from random import randint, random
from instaloader import Post, Profile
import datetime
import os
import os.path
from os import path
import re

#####################
def pause(size):
    """Selection of different pauses"""
    # weird numbers intentional, to not look too much like a computer
    if size == 'XXS':
        pauselength = 1.1 * (random() + 0.5)  # between 0.5 sec and 1.7 sec
    elif size == 'XS':
        pauselength = 5.1 * (random() + 0.05)  # between 0.5 sec and 5 sec
    elif size == 'S':
        pauselength = 15.4 * (random() + 0.1)  # between 1.5 sec and 15 sec
    elif size == 'M':
        pauselength = 50.7 * (random() + 0.1)  # between 5 sec and 1 min
    elif size == 'L':
        pauselength = 1.6 * 151.3 * (random() + 0.25)  # between 1.6 *( 37 sec and 3.15 min)
    elif size == 'XL':
        pauselength = 141.3 * (random() + 0.21) + 272  # between 5.02 and 7.38 min
    elif size == 'XXL':
        pauselength = 3130 * (random() + 0.05) + 412  # between 9.475 and 61.6 min

    print('|    Pausing for: ', round(pauselength / 60.0, 1), ' minutes')
    time.sleep(pauselength)


def merge(list1, list2):
    """Merges two list into a list of tuples"""
    merged_list = [(list1[i], list2[i]) for i in range(0, len(list1))]
    return merged_list

#####################



class RandomDriver(webdriver.Firefox, webdriver.Chrome):
    """Randomly picks a Firefox or Chrome, is designed to be used in a context manager"""
    def __init__(self):
        # randomly picking a different webdriver, trying to avoid anti-crawler detection by Instagram
        driverchoice = ['Chrome', 'Firefox'][randint(0, 1)]
        if driverchoice == 'Chrome':
            webdriverPath = homePath + '/chromedriver'  # chrome driver
            self.driver = webdriver.Chrome.__init__(self, executable_path=webdriverPath)
        elif driverchoice == 'Firefox':
            webdriverPath = homePath + '/geckodriver'  # chrome driver
            self.driver = webdriver.Firefox.__init__(self, executable_path=webdriverPath)

    def __exit__(self):
        self.driver.quit()

class Database:
    """The SQLite3 database. This class also keeps a list of post urls that have not yet been scrapped.
    This class should also be used with a context manager"""
    def __init__(self, databasePath):
        self.databasePath = databasePath

    def __enter__(self):
        if path.exists(self.databasePath):
            self.connection = sqlite3.connect(self.databasePath)
            self.cursor = self.connection.cursor()
        else:
            self.connection = sqlite3.connect(self.databasePath)
            self.cursor = self.connection.cursor()
            self.createDatabaseTabe()
        self.NonDownloadedPosts = []
        self.NonDownloadedPosts.extend(self.getNonDownloadedPosts())
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.connection.close()

    def close(self): # just in case you don't use context managers
        self.connection.close()

    def createDatabaseTabe(self):
        """Creates a Table when used for the first time"""
        with self.connection: # this way, it is either committed upon success or rolled back otherwise
            self.cursor.execute("""CREATE TABLE IF NOT EXISTS photo (
                        photo_id INTEGER PRIMARY KEY AUTOINCREMENT,
                        photo_name TEXT,
                        photo_url TEXT, 
                        likes TEXT,
                        age TEXT, 
                        downloaded TEXT, 
                        IG_category TEXT, 
                        hashtags TEXT,
                        photographer_name TEXT,
                        followers TEXT,
                        following TEXT,
                        manually_confirmed TEXT,
                        is_downloaded TEXT 
                        )""")

    def writeMetadataToDb(self, userpost):
        """Updates a post that already exists in the database with post-metadata"""
        with Database(self.databasePath) as db:
            db.cursor.execute("SELECT photo_id FROM photo WHERE photo_url = ? ", (userpost.getPostUrl(),))
            photo_id = db.cursor.fetchall()[0][0]
            #print("|    Using following ID: ", photo_id)
            #print("|    metadata is:", userpost.metadata)
            # write metadata into DB
            shortcode = userpost.metadata['photo_url'].split('/')[-2]
            db.cursor.execute("UPDATE photo SET photo_name = ? WHERE photo_id = ?;", (str(shortcode), photo_id))
            db.cursor.execute("UPDATE photo SET likes = ? WHERE photo_id = ?;", (str(userpost.metadata['likes']), photo_id))
            db.cursor.execute("UPDATE photo SET age = ? WHERE photo_id = ?;", (str(userpost.metadata['age']), photo_id))
            db.cursor.execute("UPDATE photo SET downloaded = ? WHERE photo_id = ?;", (str(userpost.metadata['downloaded']), photo_id))
            db.cursor.execute("UPDATE photo SET IG_category = ? WHERE photo_id = ?;", (str(userpost.metadata['IG_category']), photo_id))
            db.cursor.execute("UPDATE photo SET hashtags = ? WHERE photo_id = ?;", (str(userpost.metadata['hashtags']), photo_id))
            db.cursor.execute("UPDATE photo SET followers = ? WHERE photo_id = ?;", (str(userpost.metadata['followers']), photo_id))
            db.cursor.execute("UPDATE photo SET following = ? WHERE photo_id = ?;", (str(userpost.metadata['following']), photo_id))
            db.connection.commit()

    def createPostEntryInDatabase(self, userpost):
        """inserts new post to database at the end of the database (with url and photographer name being non-empty)"""
        default_confirmedLandscapeShot = 'False'
        default_isDownloaded = 'False'
        newId = self.__createDatabaseId()
        with self.connection:
            self.cursor.execute("INSERT OR REPLACE INTO photo VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (newId,
                str(userpost.metadata['photo_name']),
                str(userpost.metadata['photo_url']),
                str(userpost.metadata['likes']),
                str(userpost.metadata['age']),
                str(userpost.metadata['downloaded']),
                str(userpost.metadata['IG_category']),
                str(userpost.metadata['hashtags']),
                str(userpost.metadata['photographer_name']),
                str(userpost.metadata['followers']),
                str(userpost.metadata['following']),
                str(default_confirmedLandscapeShot),
                str(default_isDownloaded)
                ))

    def __createDatabaseId(self):
        """creates an integer that is one larger than the largest primary index"""
        with self.connection:
            self.cursor.execute("SELECT MAX(photo_id) FROM photo")
            try:
                maxId = int(self.cursor.fetchone()[0])
                newId = maxId + 1
            except:
                newId = 1
            return newId

    def getNonDownloadedPosts(self):
        """Gets all post urls from DB that have not yet been downloaded"""
        self.cursor.execute('''SELECT photo_url FROM photo WHERE is_downloaded == "False";''')
        return self.cursor.fetchall()

    def getMetadataNonDownloadedPosts(self):
        """Gets Metadata from DB that have not yet been downloaded"""
        self.cursor.execute('''SELECT * FROM photo WHERE is_downloaded == "False";''')
        return self.cursor.fetchall()

    #def getNonDownloadedPosts_userNames(self):
    #    """Gets all photographer_names from posts in the DB that have not yet been downloaded"""
    #   self.cursor.execute('''SELECT photographer_name FROM photo WHERE is_downloaded == "False";''')
    #    return self.cursor.fetchall()

    def getNumberPosts(self):
        """Gets number of all posts from DB"""
        self.cursor.execute('''SELECT * FROM photo;''')
        numPosts = len(self.cursor.fetchall())
        return numPosts

    def getNumberNonDownloadedPosts(self):
        """Gets number of all posts from DB that have not yet been downloaded"""
        self.cursor.execute('''SELECT is_downloaded FROM photo WHERE is_downloaded == "False";''')
        NumNotDownloaded = len(self.cursor.fetchall())
        return NumNotDownloaded

    def getNumberDownloadedPosts(self):
        """Gets number of all posts from DB that have not yet been downloaded"""
        self.cursor.execute('''SELECT is_downloaded FROM photo WHERE is_downloaded == "True";''')
        NumDownloaded = len(self.cursor.fetchall())
        return NumDownloaded

    def writePictureSavedFlag(self, userpost):
        with self.connection:
            # identify the DB ID of the post url
            self.cursor.execute("SELECT photo_id FROM photo WHERE photo_url = ? ", (userpost.getPostUrl(),))
            photo_id = self.cursor.fetchall()[0][0]
            self.cursor.execute("UPDATE photo SET is_downloaded = ? WHERE photo_id = ?;", ('True', photo_id))
            #print("|    Updated the saving event to the database")

    def identifyIfUrlIsInDatabase(self, postUrl):
        self.cursor.execute("SELECT photo_url FROM photo WHERE photo_url = (?);", (postUrl,))
        similar_link = self.cursor.fetchall()
        return len(similar_link) != 0

    def removePostFromDb(self, userpost):
        with self.connection:
            self.cursor.execute("DELETE FROM photo WHERE photo_url = (?);", (userpost.getPostUrl(),))

    def printStatus(self):
        print("|    Number of posts in DB: ", self.getNumberPosts())
        print("|    Number of posts to download: ", self.getNumberNonDownloadedPosts())
        print("|    Number of posts downloaded: ",  self.getNumberDownloadedPosts())

class Userprofile:
    def __init__(self, homePath, databasePath, UserListPath):
        self.homePath = homePath
        self.driver = None
        self.userName = ''
        self.databasePath = databasePath
        self.UserListPath = UserListPath
        self.__getRandomUser() # writes random username (from 'UserList.txt') into self.userName
        self.userUrl = "https://www.instagram.com/" + self.userName + "/"
        self.postUrls = []

    def visitProfile(self):
        print("|    Profile name: ",self.userName)
        self.driver = RandomDriver()
        self.driver.get(self.userUrl)

    def scroll(self):
        scroll_down = "window.scrollTo(0, document.body.scrollHeight);"
        self.driver.execute_script(scroll_down)
        pause('XXS')

    def getListOfPresentPosts(self):
        try:
            links = [a.get_attribute('href') for a in self.driver.find_elements_by_tag_name('a')]
        except:
            links = []
        postList = []
        for link in links:
            post = 'https://www.instagram.com/p/'
            if post in link:
                postList.append(link)
        return(postList)

    def __getRandomUser(self):
        try:
            with open(self.UserListPath, 'r') as openedFile: # open txt file
                allUsers = openedFile.readlines()
        except:
            print("Cannot locate the UserList.txt file")
        totalNames = len(allUsers)
        randomNo = randint(0, totalNames - 1)
        randomUsername = allUsers[randomNo].replace('/', '') # will throw the dice which user to pick
        randomUsername = randomUsername.rstrip()
        self.userName = randomUsername

    def isolateUniquePostFromList(self, postList):
        postListUnique = []
        with Database(self.databasePath) as db:
            for postUrl in postList:
                if not db.identifyIfUrlIsInDatabase(postUrl):
                    postListUnique.append(postUrl)
        return postListUnique

    def getName(self):
        return self.userName

class Userpost:

    def __init__(self, homePath, DatabaseFolder,  postUrl, userName):
        self.homePath = homePath
        self.driver = None
        self.DatabaseFolder = DatabaseFolder
        self.postIsVideo = False
        self.metadata = {
            'photo_id' : None,
            'photo_name': '',
            'photo_url': postUrl,
            'likes': '',
            'age': '',
            'downloaded': '',
            'IG_category': '',
            'hashtags': '',
            'photographer_name': userName,
            'followers': '',
            'following': '',
            'manually_confirmed': '',
            'is_downloaded': '',
                        }

    def __startInstaloaderInstance(self):
        shortcode = self.metadata['photo_url'].split('/')[-2]
        a = self.DatabaseFolder[:] # make copy, don't mess with the original
        db_folder = a.replace(self.homePath, '')
        folderpath = db_folder[1:] + self.metadata['photographer_name']

        L = instaloader.Instaloader(filename_pattern='{shortcode}',
                                    dirname_pattern= folderpath,
                                    download_videos=False,
                                    download_video_thumbnails=False,
                                    compress_json = False,
                                    save_metadata = False,
                                    download_comments = False,
                                    post_metadata_txt_pattern = '')
        return L

    def downloadPic(self):
        L = self.__startInstaloaderInstance()
        shortcode = self.metadata['photo_url'].split('/')[-2]
        profile = Profile.from_username(L.context, self.metadata['photographer_name'])
        post = Post.from_shortcode(L.context, shortcode)
        if post.is_video:
            self.postIsVideo = True
        try:
            picture_save_flag = L.download_post(post, target='DB' + profile.username, )
        except:
            picture_save_flag = False
        return picture_save_flag

    def confirmPresenceOfJpg(self):
        shortcode = self.metadata['photo_url'].split('/')[-2]
        path = self.DatabaseFolder + self.metadata['photographer_name']
        isInDB = os.path.isfile(path + '/' + shortcode + '.jpg')
        #print("path to jpg ", path + '/' + shortcode + '.jpg')
        print("|    JPG present: ? ", isInDB)
        return isInDB


    def downloadMetadata(self):
        L = self.__startInstaloaderInstance()
        shortcode = self.metadata['photo_url'].split('/')[-2]
        profile = Profile.from_username(L.context, self.metadata['photographer_name'])
        post = Post.from_shortcode(L.context, shortcode)
        data_profile = profile._asdict()  # accessing the metadata dict from the profile structure, UGLY
        data_post = post._asdict()  # accessing the metadata dict from the post structure, UGLY
        metadata = {}
        metadata['photo_url'] = self.metadata['photo_url']
        metadata['likes'] = post.likes
        ## TOO LONG STILL
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
        ## TOO LONG STILL
        metadata['downloaded'] = str(datetime.datetime.now())
        # get image descriptions
        try:
            metadata['IG_category'] = \
            data_post['edge_sidecar_to_children']['edges'][0]['node']['accessibility_caption'].split(
                'Image may contain:')[1].split("\n")[0]
        except:
            metadata['IG_category'] = ''
        hashtags_original = post.caption_hashtags  # reformating into one string with '#' in front
        hashtags = []
        for tags in hashtags_original:
            hashtags.append('#' + tags)
        hashtags_str = str(hashtags).replace(",", "").replace("'", "").replace("[", "").replace("]", "")
        metadata['hashtags'] = hashtags_str
        metadata['photographer_name'] = data_post['owner']['username']
        metadata['followers'] = data_post['owner']['edge_followed_by']['count']
        metadata['following'] = data_profile['edge_follow']['count']
        metadata['photo_name'] = shortcode
        metadata['is_downloaded'] = True # this method is only used for saved posts
        self.metadata = metadata
        print('|    Metadata was scrapped')
        return metadata

    def getUsername(self):
        return self.metadata['photographer_name']

    def getPostUrl(self):
        return self.metadata['photo_url']

    def removeTrailingMulitimages(self): # does not modify the jpg of a 'single-image-post"
        jpgpath = self.DatabaseFolder + self.metadata['photographer_name'] + '/'
        files = []
        shortcode = self.metadata['photo_url'].split('/')[-2]
        for i in os.listdir(jpgpath):
            if os.path.isfile(os.path.join(jpgpath, i)) and shortcode in i:
                files.append(i) # list of all the jpgs with that shortcode. Longer than 1 entry when multiimage
        if files:
            try:
                # Will keep the first image, delete the trailing ones
                indexFirstjpg = files.index(shortcode + '_1.jpg') # unfortunately, index is a clunky method!!!
            except:
                indexFirstjpg = 0
            os.rename(jpgpath + '/' + files[indexFirstjpg], jpgpath + '/' + shortcode + '.jpg')  # rename the first image to its shortcode name.
            # This is neutral for normal, non-multiimages, does not effectively change its name
            if len(files) >= 2: # multiimage
                a = range(0,len(files))
                indicesTrailingimages = [x for i, x in enumerate(a) if i != indexFirstjpg]
                for i in indicesTrailingimages:
                    os.remove(jpgpath + '/' + files[i])  # delete all but the first multiimage

class ScrappApp:

    def __init__(self, homePath, databasePath, databaseFolder,  UserListPath):
        self.homePath = homePath
        self.databasePath = databasePath
        self.UserListPath = UserListPath
        self.databaseFolder = databaseFolder
        self.startScrapping = datetime.datetime.now()
        self.maxRuntime = 10
        self.minimumNumUrlsPresent = 9

    def scrapUniquePostsToDb(self, userprofile):
        photographerName = userprofile.getName()
        postList = userprofile.getListOfPresentPosts()
        urlListUnique = userprofile.isolateUniquePostFromList(postList)
        for ulr in urlListUnique:  # list of tuple, first: url, second: userName
            p = Userpost(self.homePath, self.databaseFolder, ulr, photographerName)
            with Database(self.databasePath) as db:
                db.createPostEntryInDatabase(p)

    def getUrlListUnique(self):
        """Gets a list of Instagram post urls that are not yet in the database"""
        with Database(self.databasePath) as db:
            NumberNonDownloadedPosts = db.getNumberNonDownloadedPosts()
        while NumberNonDownloadedPosts < self.minimumNumUrlsPresent: # are there enough posts to download?
            userprofile = Userprofile(self.homePath, self.databasePath, self.UserListPath)
            userprofile.visitProfile()
            time.sleep(3)
            self.scrapUniquePostsToDb(userprofile)
            with Database(self.databasePath) as db:
                NumberNonDownloadedPosts = db.getNumberNonDownloadedPosts()
            if NumberNonDownloadedPosts < self.minimumNumUrlsPresent: # are there enough posts to download?
                randomScrollNumber = randint(1, 8)
                for i in range(randomScrollNumber):
                    with Database(self.databasePath) as db:
                        NumberNonDownloadedPosts = db.getNumberNonDownloadedPosts()
                    if NumberNonDownloadedPosts < self.minimumNumUrlsPresent: # are there enough posts to download?
                        print("|    scrolling")
                        userprofile.scroll()
                        self.scrapUniquePostsToDb(userprofile)
        print("|    sufficient posts")
        with Database(self.databasePath) as db:
            MetadataNonDownloadedPosts = db.getMetadataNonDownloadedPosts()
        return MetadataNonDownloadedPosts

    def endConditionReached(self):
        duration_run = datetime.datetime.now() - self.startScrapping
        duration_run_minutes = round(duration_run.total_seconds() / 60, 2)
        EndconditionReached = duration_run_minutes > self.maxRuntime
        if EndconditionReached:
            print("Scrapping run is done")
            print("Current time:", datetime.datetime.now())
        return EndconditionReached

    def run(self):

        while not self.endConditionReached():
            print("")
            print("_____ MODULE 1__________")
            print("GET PHOTO URLS")
            print("_____ MODULE 1__________")
            print("|")
            MetadataNonDownloadedPosts = self.getUrlListUnique()
            p = [] # list of posts to scrap
            for m in MetadataNonDownloadedPosts:
                p.append(Userpost(self.homePath, self.databaseFolder, m[2], m[8])) # first: url, second: userName, check structure of metadata
            print("__")
            print("")
            ####################
            print("_____ MODULE 2.1__________")
            print("VISIT RANDOM PHOTO URL (scrap image)")
            print("_____ MODULE 2.1__________")
            print("|")
            randIndex = randint(0, len(p) - 1)             #pick post
            userpost = p[randIndex]
            print("| Database status before")
            with Database(self.databasePath) as db:
                db.printStatus()
            print("saving Post: ", userpost.getPostUrl(), " (Username: ", userpost.getUsername(),")")
            #userpost = Userpost(self.homePath, 'https://www.instagram.com/p/CAqQ0QsAZZW/', 'danielkordan')
            saveSuccesful = userpost.downloadPic()
            print("|    Saving succesful: ", saveSuccesful)
            if userpost.postIsVideo:
                print('|    post could not be saved, it was a video')
            if saveSuccesful:
                with Database(self.databasePath) as db:
                    db.writePictureSavedFlag(userpost)
                userpost.removeTrailingMulitimages()
                JPEGpresent = userpost.confirmPresenceOfJpg()
            #pause("S")
            print("__")
            print("")
            ####################
            print("_____ MODULE 2.2__________")
            print("VISIT RANDOM PHOTO URL (scrap metadata)")
            print("_____ MODULE 2.2__________")
            print("|")
            if saveSuccesful and JPEGpresent:
                userpost.downloadMetadata()
                with Database(self.databasePath) as db:
                    db.writeMetadataToDb(userpost)
            if userpost.postIsVideo: # remove from DB
                with Database(self.databasePath) as db:
                    db.removePostFromDb(userpost)
                print("|    will remove post from DB, is Video")
            print("| Database status after")
            with Database(self.databasePath) as db:
                db.printStatus()
            print("|    Current time:", datetime.datetime.now())
            print("__")
            print("")
            pause('L')
            if random() < 0.12:
                pause('L')


        print("DONE")




homePath = '/Users/Peterg/code/IgScrapper'
databaseFolder = homePath + '/Database_img/'
databasePath = databaseFolder + 'IGdata.db'
UserListPath = homePath + '/UserList.txt'
scrapper = ScrappApp(homePath, databasePath, databaseFolder, UserListPath)
scrapper.run()




