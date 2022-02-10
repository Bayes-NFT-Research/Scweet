# from . import utils
import utils
from time import sleep
import random
import pandas as pd
import json
import csv
import datetime
from utils import init_driver, get_last_date_from_csv, log_search_page, keep_scroling, dowload_images


def get_user_information(users, driver=None, headless=True):
    """ get user information if the "from_account" argument is specified """

    driver = utils.init_driver(headless=headless)

    users_info = {}
    if type(users) == str:
        users = [users]
    for i, user in enumerate(users):
        log_user_page(user, driver)
        if user is not None:

            try:
                following = driver.find_element_by_xpath(
                    '//a[contains(@href,"/following")]/span[1]/span[1]').text
                followers = driver.find_element_by_xpath(
                    '//a[contains(@href,"/followers")]/span[1]/span[1]').text
            except Exception as e:
                print(e)
                return

            try:
                element = driver.find_element_by_xpath('//div[contains(@data-testid,"UserProfileHeader_Items")]//a[1]')
                website = element.get_attribute("href")
            except Exception as e:
                print(e)
                website = ""

            try:
                desc = driver.find_element_by_xpath('//div[contains(@data-testid,"UserDescription")]').text
            except Exception as e:
                print(e)
                desc = ""
            a = 0
            try:
                join_date = driver.find_element_by_xpath(
                    '//div[contains(@data-testid,"UserProfileHeader_Items")]/span[3]').text
                birthday = driver.find_element_by_xpath(
                    '//div[contains(@data-testid,"UserProfileHeader_Items")]/span[2]').text
                location = driver.find_element_by_xpath(
                    '//div[contains(@data-testid,"UserProfileHeader_Items")]/span[1]').text
            except Exception as e:
                print(e)
                try:
                    join_date = driver.find_element_by_xpath(
                        '//div[contains(@data-testid,"UserProfileHeader_Items")]/span[2]').text
                    span1 = driver.find_element_by_xpath(
                        '//div[contains(@data-testid,"UserProfileHeader_Items")]/span[1]').text
                    if hasNumbers(span1):
                        birthday = span1
                        location = ""
                    else:
                        location = span1
                        birthday = ""
                except Exception as e:
                    print(e)
                    try:
                        join_date = driver.find_element_by_xpath(
                            '//div[contains(@data-testid,"UserProfileHeader_Items")]/span[1]').text
                        birthday = ""
                        location = ""
                    except Exception as e:
                        print(e)
                        join_date = ""
                        birthday = ""
                        location = ""
            print("--------------- " + user + " information : ---------------")
            print("Following : ", following)
            print("Followers : ", followers)
            print("Location : ", location)
            print("Join date : ", join_date)
            print("Birth date : ", birthday)
            print("Description : ", desc)
            print("Website : ", website)
            users_info[user] = [following, followers, join_date, birthday, location, website, desc]

            if i == len(users) - 1:
                driver.close()
                return users_info
        else:
            print("You must specify the user")
            continue


def log_user_page(user, driver, headless=True):
    sleep(random.uniform(1, 2))
    driver.get('https://twitter.com/' + user)
    driver.implicitly_wait(10)


def get_users_followers(users, env, verbose=1, headless=True, wait=2, limit=float('inf'), file_path=None):
    followers = utils.get_users_follow(users, headless, env, "followers", verbose, wait=wait, limit=limit)

    if file_path == None:
        file_path = 'outputs/' + str(users[0]) + '_' + str(users[-1]) + '_' + 'followers.json'
    else:
        file_path = file_path + str(users[0]) + '_' + str(users[-1]) + '_' + 'followers.json'
    with open(file_path, 'w') as f:
        json.dump(followers, f)
        print(f"file saved in {file_path}")
    return followers


def get_users_following(users, env, verbose=1, headless=True, wait=2, limit=float('inf'), file_path=None):
    following = utils.get_users_follow(users, headless, env, "following", verbose, wait=wait, limit=limit)

    if file_path == None:
        file_path = 'outputs/' + str(users[0]) + '_' + str(users[-1]) + '_' + 'following.json'
    else:
        file_path = file_path + str(users[0]) + '_' + str(users[-1]) + '_' + 'following.json'
    with open(file_path, 'w') as f:
        json.dump(following, f)
        print(f"file saved in {file_path}")
    return following


def get_users_tweets(users, driver=None, headless=True, interval=5, since=None, until=None, limit=float("inf")):
    driver = utils.init_driver(headless=headless)
    if type(users) == str:
        users = [users]
    for i, user in enumerate(users):
        log_user_page(user, driver)
        if user is not None:
            header = ['UserScreenName', 'UserName', 'Timestamp', 'Text', 'Embedded_text', 'Emojis', 'Comments', 'Likes',
                      'Retweets',
                      'Image link', 'Tweet URL']
            # list that contains all data 
            data = []
            # unique tweet ids
            tweet_ids = set()
            # write mode 
            write_mode = 'w'
            # start scraping from <since> until <until>
            # add the <interval> to <since> to get <until_local> for the first refresh
            # until_local = datetime.datetime.strptime(since, '%Y-%m-%d') + datetime.timedelta(days=interval)
            # if <until>=None, set it to the actual date
            # if until is None:
            #     until = datetime.date.today().strftime("%Y-%m-%d")
            # set refresh at 0. we refresh the page for each <interval> of time.
        refresh = 0
        scroll = 0
        # with open("./backup.csv", write_mode, newline='', encoding='utf-8') as f:
        #     writer = csv.writer(f)
        #     if write_mode == 'w':
        #         # write the csv header
        #         writer.writerow(header)
        # log search page for a specific <interval> of time and keep scrolling unltil scrolling stops or reach the <until>
        while scroll <= limit:
            # number of scrolls
            # number of logged pages (refresh each <interval>)
            refresh += 1
            # number of days crossed
            # days_passed = refresh * interval
            # last position of the page : the purpose for this is to know if we reached the end of the page or not so
            # that we refresh for another <since> and <until_local>
            last_position = driver.execute_script("return window.pageYOffset;")
            # should we keep scrolling ?
            scrolling = True
            # number of tweets parsed
            tweet_parsed = 0
            # sleep
            sleep(random.uniform(0.5, 1.5))
            # start scrolling and get tweets
            writer = None
            driver, data, writer, tweet_ids, scrolling, tweet_parsed, scroll, last_position = \
                keep_scroling(driver, data, writer, tweet_ids, scrolling, tweet_parsed, limit, scroll, last_position)

    data = pd.DataFrame(data, columns=['UserScreenName', 'UserName', 'Timestamp', 'Text', 'Embedded_text', 'Emojis',
                                       'Comments', 'Likes', 'Retweets', 'Image link', 'Tweet URL'])
    return data


def hasNumbers(inputString):
    return any(char.isdigit() for char in inputString)


if __name__ == "__main__":
    get_users_tweets('WhiteWhaleTerra', headless=False)
