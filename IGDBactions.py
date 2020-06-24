import datetime
import sqlite3
import sys
sys.path.append('Users/Peterg/Documents/Python/Instabot')
sys.path.append('Users/Peterg/Documents/Python/IG_data')
import re

def create_photographer_db_entry(connection, cursor):
    with connection:
        command1 = """CREATE TABLE IF NOT EXISTS
        photographer(
        photographer_id INT PRIMARY KEY AUTOINCREMENT
        photographer_name TEXT, 
        followers TEXT, 
        following TEXT
        )"""
        cursor.execute(command1)


def create_photo_db_entry(connection, cursor):
    with connection:
        cursor.execute("""CREATE TABLE IF NOT EXISTS photo (
                        photo_id INTEGER PRIMARY KEY AUTOINCREMENT,
                        photo_name TEXT,
                        photo_url TEXT, 
                        likes TEXT,
                        age TEXT, 
                        date_downloaded TEXT, 
                        IG_categories TEXT, 
                        hashtags TEXT,
                        photographer_name TEXT,
                        followers TEXT,
                        following TEXT,
                        manually_confirmed TEXT,
                        is_downloaded TEXT 
                        )""")

def insertPhotoInDB(connection, cursor, photo_name, post_link, likes, age_inDays, datenow, im_description, post_hastags, user_tocheck, follower_no, followee_no):
    with connection:
        # first create an integer, which is one larger than the largest INT id:
        cursor.execute("SELECT photo_id FROM photo")
        database_Id_list_asstring = re.findall('\d+', str(cursor.fetchall())) # gets all photo_id INTS as list
        database_ID = [int(i) for i in database_Id_list_asstring]
        if database_ID:
            newID = int(int(max(database_ID)) + 1)
            #print('currently so many entries', int(max(database_ID)))
        else:
            newID = 1
        print("database ID is: ", newID)
        default_usercheck = 'False'
        default_isdownloaded = 'False'
        cursor.execute("INSERT OR REPLACE INTO photo VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
                       , (newID, str(photo_name), str(post_link), str(likes),
                          str(age_inDays), str(datenow), str(im_description), str(post_hastags),
                          str(user_tocheck), str(follower_no), str(followee_no), str(default_usercheck), str(default_isdownloaded)))


def removeIfAlreadyInDatabase(post_links, cursor):
    post_links_entries_before_removal = len(post_links)
    cursor.execute("SELECT photo_url FROM photo")
    results = cursor.fetchall()
    for db_url in results: # strategy: in the post_links list, try to remove each entry already in database
        try: # element of post_link exists in database -> remove in post_links
            db_url_string = str(db_url)[2:-3] # getting rid of the : '( , ) stuff
            post_links.remove(db_url_string)
        except: # element of post_link does not exist in database -> leave in post_links
            pass
    post_links_entries_after_removal =  len(post_links)
    print('|    Original number of identified posts: ', post_links_entries_before_removal, ' and after ' \
         'removing duplicates: ', post_links_entries_after_removal)
    return post_links


def getNumberNotDownloaded(connection, cursor):
    cursor.execute("SELECT is_downloaded FROM photo")
    database_Id_list_asstring = re.findall('False', str(cursor.fetchall()))
    number_not_downloaded = 0
    for entry in database_Id_list_asstring:
        if entry == 'False':
            number_not_downloaded = number_not_downloaded + 1
    return number_not_downloaded


def getNumberMetadataNotDownloaded(connection, cursor):
    cursor.execute("SELECT likes FROM photo")
    database_Id_list_asstring = re.findall('None', str(cursor.fetchall()))
    number_metadata_not_downloaded = 0
    for entry in database_Id_list_asstring:
        if entry == 'None':
            number_metadata_not_downloaded = number_metadata_not_downloaded + 1
    return number_metadata_not_downloaded


def getDBStatus(connection, cursor):
    cursor.execute("SELECT * FROM photo ")
    results = cursor.fetchall()
    numDbEntries = len(results)
    numImgNotDownloaded = getNumberNotDownloaded(connection, cursor)
    numImgMetadataNotDownloaded = getNumberMetadataNotDownloaded(connection, cursor)
    print('|    Number of picture urls: ', numDbEntries, '\n'
            '|    Number of pictures where Metadata is not downloaded: ', numImgMetadataNotDownloaded, '\n'
            '|    Number of pictures not downloaded: ', numImgNotDownloaded)
    return numDbEntries, numImgMetadataNotDownloaded, numImgNotDownloaded