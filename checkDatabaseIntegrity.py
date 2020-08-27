import sqlite3
import os

homePath = '/Users/Peterg/code/IgScrapper/Database_img'
DBname = '/IGdata.db'

def removeEmptyListentries(lst):
    return list(filter(None, lst))

def convertListOfTuplesToList(tuple):
    lst = map(lambda x: x[0], tuple)
    lst = list(lst)
    return lst

def flagImageAsNondownloaded(photo_name):
    connection = sqlite3.connect(homePath + DBname)
    cursor = connection.cursor()
    cursor.execute("UPDATE photo SET is_downloaded = ? WHERE photo_name = ?;", ('False', photo_name))
    connection.commit()
    connection.close()


def getListOfImagesFlaggedForDownloaded():
    connection = sqlite3.connect(homePath + DBname)
    cursor = connection.cursor()
    cursor.execute('''SELECT photo_name FROM photo WHERE is_downloaded == "True";''')
    FlaggedForDownloaded = cursor.fetchall()
    FlaggedForDownloaded = convertListOfTuplesToList(FlaggedForDownloaded)
    FlaggedForDownloaded = removeEmptyListentries(FlaggedForDownloaded)
    NumDownloaded = len(FlaggedForDownloaded)
    connection.close()
    return NumDownloaded, FlaggedForDownloaded


def getListOfJpgsWithoutMetadata():
    connection = sqlite3.connect(homePath + DBname)
    cursor = connection.cursor()
    cursor.execute('''SELECT photo_name FROM photo WHERE is_downloaded == "True" AND downloaded == "None";''')
    ListOfJpgsWithoutMetadata = cursor.fetchall()
    NumListOfJpgsWithoutMetadata = len(ListOfJpgsWithoutMetadata)
    ListOfJpgsWithoutMetadata = convertListOfTuplesToList(ListOfJpgsWithoutMetadata)
    ListOfJpgsWithoutMetadata = removeEmptyListentries(ListOfJpgsWithoutMetadata)
    connection.close()
    return NumListOfJpgsWithoutMetadata, ListOfJpgsWithoutMetadata


def identifyIfUrlIsInDatabase(photo_name):
    """Checks if this photo_name is already in the database by comparing its photo_name to all photo_names saved in the database"""
    connection = sqlite3.connect(homePath + DBname)
    cursor = connection.cursor()
    cursor.execute("SELECT photo_name FROM photo WHERE photo_name == (?);", (photo_name,))
    similar_link = cursor.fetchall()
    return len(similar_link) != 0


def removePostFromDb(photo_name):
    """Deletes a post from the database, by comparing its URL to all URLs saved in the ddatabase"""
    connection = sqlite3.connect(homePath + DBname)
    cursor = connection.cursor()
    cursor.execute("DELETE FROM photo WHERE photo_name == (?);", (photo_name,))


def confirmPresenceOfJpg(photo_name):
    """ Checks if the jpg belonging to this post is present
    This method will not work for multiimages, since it
    checks for shortcode + '.jpg', while multiimages are called
    shortcode + '_1.jpg', shortcode + '_2.jpg' etc
    RUN THIS AFTER removeTrailingMulitimages(self) !!!!
    """
    shortcode = photo_name
    connection = sqlite3.connect(homePath + DBname)
    cursor = connection.cursor()
    cursor.execute("SELECT photographer_name FROM photo WHERE photo_name == (?);", (photo_name,))
    photographer_name_tupule = cursor.fetchall()
    photographer_name = convertListOfTuplesToList(photographer_name_tupule)[0].rstrip()
    connection.close()
    path = homePath + '/' + photographer_name
    isInDB = os.path.isfile(path + '/' + shortcode + '.jpg')
    return isInDB


def main():
    NumDownloaded, FlaggedForDownloaded = getListOfImagesFlaggedForDownloaded()
    print("ImagesFlaggedAsDownloaded: ", NumDownloaded)
    isDownloaded = []
    jpgNotPresent = []
    for photo in FlaggedForDownloaded:
        jpgThere = confirmPresenceOfJpg(photo)
        if not jpgThere:
            jpgNotPresent.append(photo)
        isDownloaded.append(jpgThere)

    print("Total images present: ", sum(isDownloaded))
    print("Jpegs not present: ", jpgNotPresent)

    NumListOfJpgsWithoutMetadata, ListOfJpgsWithoutMetadata = getListOfJpgsWithoutMetadata()
    print("Number of jpgs without Metadata:", NumListOfJpgsWithoutMetadata)
    print("Jpgs without Metadata:", ListOfJpgsWithoutMetadata)
    print("flagging non-present jpgs as non-downloaded")
    for post in jpgNotPresent:
        print(post)
        flagImageAsNondownloaded(post)

    for post in ListOfJpgsWithoutMetadata:
        flagImageAsNondownloaded(post)




if __name__ == "__main__":
    main()
