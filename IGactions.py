# module of interactions on Instagram
# June 2020

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup as b
import time
import datetime
from random import random
from random import randint
import login
from pathlib import Path
import urllib.request
import urllib
import re
import sys


def pause(size):
    # weird numbers intentional, to not look too much like a computer
    if size == 'XS':
        pauselength = 1.1 * (random() + 0.05)
    elif size == 'S':
        pauselength = 3.3 * (random() + 0.1)
    elif size == 'M':
        pauselength = 5.7 * (random() + 0.1)
    elif size == 'L':
        pauselength = 12.1 * (random() + 0.1)
    elif size == 'XL':
         pauselength = 11.3 * (random() + 0.21) + 22
    elif size == 'XXL':
        pauselength = 3130 * (random() + 0.05) + 412

    print('Pausing for: ', pauselength / 60.0 , ' minutes')
    time.sleep(pauselength)



def signin(driver, username, password):
    pause('M')
    l = login.Login(driver, username, password)
    pause('M')
    l.signin()

def checkForNewLikers(driver):
    try:
        newlikes_btn = WebDriverWait(driver, 10).until(EC.presence_of_element_located(
            (By.XPATH, '//*[@id="react-root"]/section/nav/div[2]/div/div/div[3]/div/div[4]/a')))
        if 'H9zXO' in newlikes_btn.get_attribute("class"):
            # print('You got a new like')
            pause('S')
            newlikes_btn.click()
            pressButton('Newfollower')
            ## scroll a bit
            pause('M')
            scroll_randomly()
    except:
        print("Exception during check for new likers")

def pressButton(driver, buttonType):
    try:
        if buttonType == 'Home' or buttonType == 'home':
            path = '//*[@id="react-root"]/section/nav/div[2]/div/div/div[1]/a'  # HOME
        elif buttonType == 'Explore' or buttonType == 'explore':
            path = '//*[@id="react-root"]/section/nav/div[2]/div/div/div[3]/div/div[3]/a'  # Explore
        elif buttonType == 'Thumbnailclose' or buttonType == 'thumbnailclose':
            path = '/html/body/div[4]/div[3]/button'  # closing thumbnail
        elif buttonType == 'Newfollower' or buttonType == 'newfollower':
            path = '//*[@id = "react-root"]/section/nav/div[2]/div/div/div[3]/div/div[4]/div/div/div[2]/div[2]/div/div/div/div/div[1]/div[2]/a'  # new follower button, that pops up after pressing the 'heart', indicating a new like / follow
        elif buttonType == 'NewLikers' or buttonType == 'lewlikers':
            path = '//*[@id="react-root"]/section/nav/div[2]/div/div/div[3]/div/div[4]/a'  # the 'heart', indicating a new like / follow
        else:
            print(" unknown button type")
        button = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH,path)))
        pause('S')
        button.click()
    except:
        print("Exception during button pressing")


def scroll_randomly(driver, size):
    if size == 'L':
        scrollEvents = randint(17, 45)
    elif size == 'S':
        scrollEvents = randint(7, 15)
    currentscrollY = driver.execute_script('return window.pageYOffset;')
    try:
        for h in range(scrollEvents):
            time.sleep(random() + 0.045)
            if random() < 0.15:
                time.sleep(3 + random())
            # print('scrolling')
            # print(h)
            driver.execute_script(
                "window.scrollTo(0, {})".format(str(currentscrollY + (h + 1) * 98 + randint(42, 287))))
    except:
        print("Exception during scrolling")


def count_thumbnails(driver):
    try:
        thmb_outerpath = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '#react-root > section > main >div')))
        thmb_outerpath_innerHTML = b(thmb_outerpath.get_attribute('innerHTML'), 'html.parser')
        tumbnails = thmb_outerpath_innerHTML.findAll('div', {'class': 'QzzMF Igw0E IwRSH eGOV_ _4EzTm'})
        openthumbnails_number = str(tumbnails).count('QzzMF Igw0E IwRSH eGOV_ _4EzTm')
    except:
        print("Exception during thumbnails counting")
        openthumbnails_number = 0
    return openthumbnails_number

def click_coolthumbnail(self, driver):
    try:
        max_rows = int(self.__count_thumbnails(driver) / 3)  # there are 3 collums
        collum = randint(1, 3)  # between 1 and 3
        row = randint(1, 3)  # between 1 and 3 # OLD, did not work round(0.85 * max_rows)
        # print(collum)
        # print(row)
        # print('//*[@id="react-root"]/section/main/div/div[2]/div/div[{0}]/div[{1}]'.format(str(int(row)), str(int(collum))))
        coolthumbnail = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH,
                                                                                        '//*[@id="react-root"]/section/main/div/div[2]/div/div[{0}]/div[{1}]'.format(
                                                                                            str(int(row)),
                                                                                            str(int(collum))))))
        # coolthumbnail = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH,
        #    '//*[@id="react-root"]/section/main/div/div[2]/div/div[1]/div[2]')))

        pause('M')
        coolthumbnail.click()
        pause('S')
        pause('M')
        self.__pressButton(driver, 'Thumbnailclose')  # click the close button
    except:
        print("Exception during thumbnail-pressing")

def insta_url_to_img(url, driver, user, proxy_name):
    """
    Getting the actual photo file from an Instagram url
    Args:
    url: Instagram direct post url
    filename: file name for image at url
    user: string with the IG username. Pay attention to the '/'. Use e.g. '/madspeteriversen_photography/'
    image file, saved locally
    """
    # create the object, assign it to a variable
    if proxy_name:
        proxy_url = 'https://' + proxy_name
        proxy = urllib.request.ProxyHandler({'https': proxy_url})
        # construct a new opener using your proxy settings
        opener = urllib.request.build_opener(proxy)
        # install the openen on the module-level
        urllib.request.install_opener(opener)


    if user[0] == '/':
        pass
    else:
        user = '/' + user + '/'

    target_directory = '/Users/Peterg/Documents/Python/IG_data/Database_img' +  user
    if Path('/Users/Peterg/Documents/Python/IG_data/Database_img').exists():
        if Path(target_directory).exists():
            pass
        else:
            Path(target_directory).mkdir(parents=True, exist_ok=True)
    driver.get(url)
    try: # singleimage
        xPathh = '//*[@id="react-root"]/section/main/div/div[1]/article/div[1]/div/div/div[1]/img'
        #xPathh ='//*[@id="react-root"]/section/main/div/div/article/div[1]/div/div/div[1]/img'
        image = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.XPATH,
                                                                            xPathh))).get_attribute('src').split(' ')[0]
    except: # multiimage
        try:
            xPathh = '//*[@id="react-root"]/section/main/div/div[1]/article/div[1]/div/div[1]/div[2]/div/div/div/ul/li[2]/div/div/div/div[1]/img'
            image = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.XPATH,
                                                                                xPathh))).get_attribute('src').split(' ')[0]
        except:
            xPathh = '//*[@id="react-root"]/section/main/div/div[1]/article/div[1]/div/div[1]/div[2]/div/div/div/ul/li[2]/div/div/div/div[1]/div[1]/img'
            image = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.XPATH,
                                                                                xPathh))).get_attribute('src').split(' ')[0]

    #print('Selenium cannot locate the image')
    filename = target_directory + url.split('/')[-2] + '.jpg'
    try:
        urllib.request.urlretrieve(image, filename)
        print("Saving just done")
        img_save_flag = True
    except:
        print('urllib cannot request the image')
        img_save_flag = False
        #e = sys.exc_info()[0]
        #print("<p>Error: %s</p>" % e)

    # except urllib.exceptions.MaxRetryError:
    #     print('Run into "maximum retry error", take it easy on the homepage, a break for 1 h')
    #     retry_error_break = 3660 # 1 h and 1 min, break if running into maxRetryError
    #     newscraptime = datetime.now() + datetime.timedelta(retry_error_break)
    #     print('Scrapping will resume at: ', newscraptime)
    #     time.sleep(retry_error_break)
    # else:
    #     print('Another error occured')
    if img_save_flag == True:
        print('Saved image:', filename)
    return img_save_flag
    # If image is not a photo, print notice


def getHastags(browser, post_link):
    _RE_COMBINE_WHITESPACE = re.compile(r"\s+")
    ig_variable = insta_link_details(browser, post_link)
    post_hastags = str(ig_variable['hashtags']).replace(",", "").replace("'", "").replace("[", "").replace("]", "")
    post_hastags = _RE_COMBINE_WHITESPACE.sub(" ", post_hastags).strip()
    post_hastags = '"' + post_hastags + '"'

    return post_hastags

def insta_link_details(browser, url):
    """
    Take a post url and return post details
    Args:
    urls: a list of urls for Instagram posts
    Returns:
    A list of dictionaries with details for each Instagram post, including link,
    post type, like/view count, age (when posted), and initial comment
    """

    browser.get(url)
    try:
        # This captures the standard like count.
        likes = browser.find_element_by_xpath(
            """//*[@id="react-root"]/section/main/div/div/
                article/div[2]/section[2]/div/div/button""").text.split()[0]
        post_type = 'photo'
    except:
        # This captures the like count for videos which is stored
        likes = browser.find_element_by_xpath(
            """//*[@id="react-root"]/section/main/div/div/
                article/div[2]/section[2]/div/span""").text.split()[0]
        post_type = 'video'
    age = browser.find_element_by_css_selector('a time').text
    comment = browser.find_element_by_xpath(
        """//*[@id="react-root"]/section/main/div/div/
            article/div[2]/div[1]/ul/div/li/div/div/div[2]/span""").text
    hashtags = find_hashtags(comment)
    mentions = find_mentions(comment)
    post_details = {'link': url, 'type': post_type, 'likes/views': likes,
                    'age': age, 'comment': comment, 'hashtags': hashtags,
                    'mentions': mentions}
    pause('L')
    return post_details

def find_hashtags(comment):
    """
    Find hastags used in comment and return them
    Args:
    comment: Instagram comment text
    Returns:
    a list or individual hashtags if found in comment
    """
    hashtags = re.findall('#[A-Za-z]+', comment)
    if (len(hashtags) > 1) & (len(hashtags) != 1):
        return hashtags
    elif len(hashtags) == 1:
        return hashtags[0]
    else:
        return ""

def find_mentions(comment):
    """
    Find mentions used in comment and return them
    Args:
    comment: Instagram comment text
    Returns:
    a list or individual mentions if found in comment
    """
    mentions = re.findall('@[A-Za-z]+', comment)
    if (len(mentions) > 1) & (len(mentions) != 1):
        return mentions
    elif len(mentions) == 1:
        return mentions[0]
    else:
        return ""

def getCurrentImageDescription(browser):
    _RE_COMBINE_WHITESPACE = re.compile(r"\s+")
    try:
        im_Xpath = '//*[@id="react-root"]/section/main/div/div/article/div[1]/div/div/div[1]/img'
        im_descrition_locator = WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.XPATH, im_Xpath)))
        im_description_total = im_descrition_locator.get_attribute('alt')
        im_description_total = im_description_total.replace("and", ",")
        im_description = im_description_total.split("Image may contain:", 1)[1].split(',')
        im_description = str(im_description).replace(",", "").replace("'", "").replace("[", "").replace("]", "")
        im_description = _RE_COMBINE_WHITESPACE.sub(" ", im_description).strip()
    except:
        im_description = ''
    return im_description


def getCurrentImageDescriptionMultiimage(browser):
    _RE_COMBINE_WHITESPACE = re.compile(r"\s+")
    try:
        im_Xpath = '//*[@id="react-root"]/section/main/div/div/article/div[1]/div/div[1]/div[2]/div/div/div/ul/li[2]/div/div/div/div[1]/img'
        im_descrition_locator = WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.XPATH, im_Xpath)))
        im_description_total = im_descrition_locator.get_attribute('alt')
        im_description_total = im_description_total.replace("and", ",")
        im_description = im_description_total.split("Image may contain:", 1)[1].split(',')
        im_description = str(im_description).replace(",", "").replace("'", "").replace("[", "").replace("]", "")
        im_description = _RE_COMBINE_WHITESPACE.sub(" ", im_description).strip()
    except:
        im_description = ''
    return im_description


def getUserFollowerNumber(browser):
    flw = WebDriverWait(browser, 15).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, '#react-root > section > main')))
    sflw = b(flw.get_attribute('innerHTML'), 'html.parser')
    followers = sflw.findAll('span', {'class': 'g47SY'})
    posts_no = int(followers[0].text.replace(',', ''))
    if 'k' in str(posts_no) or 'm' in str(posts_no):
        posts_no = int(str(followers[0]).split('title=')[1].split('"')[1].replace(',', ''))
    follower_no = followers[1].text.replace(',', '')
    if 'k' in str(follower_no) or 'm' in str(follower_no):
        follower_no = int(str(followers[1]).split('title=')[1].split('"')[1].replace(',', ''))
    followee_no = followers[2].text.replace(',', '')
    if 'k' in str(followee_no) or 'm' in str(followee_no):
        followee_no = int(str(followers[2]).split('title=')[1].split('"')[1].replace(',', ''))
    return posts_no, followee_no, follower_no



def loginIG(username, password, browser):
    browser.get('https://www.instagram.com/')
    uid = WebDriverWait(browser, 8).until(EC.presence_of_element_located((By.CSS_SELECTOR,
        '#react-root > section > main > article > div.rgFsT > div:nth-child(1) > div > form > div:nth-child(2) > div > label > input')))
    uid.click()
    uid.send_keys(username)
    pswd = browser.find_element_by_css_selector(
        '#react-root > section > main > article > div.rgFsT > div:nth-child(1) > div > form > div:nth-child(3) > div > label > input')
    pswd.click()
    pswd.send_keys(password)
    btn = browser.find_element_by_css_selector(
        '#react-root > section > main > article > div.rgFsT > div:nth-child(1) > div > form > div:nth-child(4)')
    btn.click()
    pause('L')


def recent_posts(username, n, browser):
    url = "https://www.instagram.com/" + username + "/"
    browser.get(url)
    post = 'https://www.instagram.com/p/'
    post_links = []
    while len(post_links) < n:
        links = [a.get_attribute('href') for a in browser.find_elements_by_tag_name('a')]
        for link in links:
            if post in link and link not in post_links:
                post_links.append(link)
        if n > 12:
            scroll_down = "window.scrollTo(0, document.body.scrollHeight);"
            browser.execute_script(scroll_down)
            pause('L')
        pause('L')
    if len(post_links) > n:
        post_links = post_links[0:n]
    return post_links


def gotoIgImage(post_links, n, browser):
    link = post_links[n]
    browser.get(link)
    pause('L')

def getIgAge(browser):
    wait = WebDriverWait(browser, 10)
    pause('M')
    elem = wait.until(
        EC.element_to_be_clickable((By.XPATH,
                    '//*[@id="react-root"]/section/main/div/div[1]/article/div[2]/div[2]/a/time')))
    age_char = elem.get_attribute("datetime")
    age_char = age_char.replace('T', ' ')
    age_char = age_char[0:-1]
    datetimeFormat = '%Y-%m-%d %H:%M:%S.%f'
    postdate = datetime.datetime.strptime(age_char, datetimeFormat)
    time_now = datetime.datetime.now()
    dt = time_now - postdate
    TimeDifferenceInHours = dt.total_seconds() / 3600.0
    TimeDifferenceInDays = TimeDifferenceInHours / 24.0
    TimeDifferenceInDays = round(TimeDifferenceInDays, 2)
    return TimeDifferenceInDays




def getIgLikes(browser):
    wait = WebDriverWait(browser, 10)
    pause('M')
    try:
        elem = wait.until(
            EC.element_to_be_clickable((By.XPATH,
                    '//*[@id="react-root"]/section/main/div/div[1]/article/div[2]/section[2]/div/div/button/span')))
        like_count = elem.text.replace(',', '')
    except:
        like_count = None
    return like_count

def get_metadata(driver, post_url):
    metadata = {}
    driver.get(post_url)

    # get likes
    metadata['likes'] = getIgLikes(driver)
    # get age
    metadata['age'] = getIgAge(driver)
    # get date now
    metadata['downloaded'] = str(datetime.datetime.now())
    # get image descriptions
    try:
        metadata['IG_category'] = getCurrentImageDescription(driver)
    except:
        metadata['IG_category'] = getCurrentImageDescriptionMultiimage(driver)
    # get hashtags
    metadata['hashtags'] = getHastags(driver, post_url)
    # get username
    # not sure yet
    return metadata
