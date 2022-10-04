import json
import pandas as pd
import requests
import sys

# Extract pageviews
def retrieve_data(id, pages):
    import time
    start = time.time()

    url = f"https://unimelb-prod.instructure.com/api/v1/users/{id}/page_views?per_page=10000"
    payload={}
    headers = {'Authorization': 'Bearer 14227~78YOvVdyFWPnz01zluLyFYIKJnlQwhdgnBWfCgirn2rGOoVgx0DzLTkBv9YBiUfW',
               'Cookie': '_csrf_token=PT0bqPvHiWgkSnBM1Fv06YkD%2FUoQR815fqC46Npy1gBaekvYqoHCCk8zOz6uA6Gg2EmqDHV%2FuhYX04vdlgj5SA%3D%3D; _legacy_normandy_session=MJirGCqnevGhMoqyKa5XPw.ziBaUp-KsTpNbr5gqqVZiF7CHRFvfspK-hSclyQq6jq5e0yxJW0H3emoyCdMF4lEe3RMwkNdBbDZh5DEnP8bbX4klJftdFOermu3YlnzAwFIuTLrjgY1l5nQL6xHcjEf.mAwOqefMhCSk9TXRjI4DoIfzzog.YoL5vg; canvas_session=MJirGCqnevGhMoqyKa5XPw.ziBaUp-KsTpNbr5gqqVZiF7CHRFvfspK-hSclyQq6jq5e0yxJW0H3emoyCdMF4lEe3RMwkNdBbDZh5DEnP8bbX4klJftdFOermu3YlnzAwFIuTLrjgY1l5nQL6xHcjEf.mAwOqefMhCSk9TXRjI4DoIfzzog.YoL5vg; log_session_id=5ca235e7d31935b950e0874e3c5b4c35'}

    keepgoing = True
    counter = 0
    res_li = []
    while keepgoing and counter <= pages:
        #  Make the call to the API URL and pass in our custom header.
        r = requests.get(url, headers=headers)

        # Make sure the call worked, and if not, we want to throw an error.
        if r.status_code != 200:
            print("ERROR: Status code returned={} for {} -- Exiting.\n".format(r.status_code, url))
            sys.exit()
        response = requests.request("GET", url, headers=headers, data=payload)
        counter += 1
    #     print(pd.json_normalize(response.json()))
        all_res = response.json()

        ress = [{'session_id': res['session_id'],
                'url': res['url'],
                'context_type': res['context_type'],
                'controller': res['controller'],
                'action': res['action'],
                'created_at': res['created_at'],
                'links': res['links']} for res in all_res]
        res_li += ress

        linkheader = r.headers['Link']
#         print(linkheader)
        # The header has an array of links, separated by commas...
        linklist = linkheader.split(",")
        # Loop through.  We're looking for the "next" link, if there is one...
        nexturl = None
        for linkitem in linklist:
            # Each link item is really two things, the actual URL, and a rel= that tells us what the link is to...
            onelink = linkitem.split(";")

            if "next" in onelink[1]:
                # Get it, strip the first character (a "<") and the last letter (a ">").
                nexturl = onelink[0]
                nexturl = nexturl[1:]
                nexturl = nexturl[:-1]

        # Now, if the nexturl is blank, set the keepgoing flag to false so we'll drop out of the loop.
        # Otherwise, set url to nexturl and we'll get the next page worth.
        if nexturl:
            url = nexturl
        else:
            keepgoing = False

    df = pd.DataFrame(res_li)
    df.to_excel(f'student_{id}_pageviews.xlsx', index=False)

    end = time.time()
    return df, end-start


# final grades
def final_grade(subjects, f):
    for s in subjects:
        url = f"https://unimelb-prod.instructure.com/api/v1/courses/{s}/enrollments?per_page=10000"
        payload={}
        headers = {'Authorization': 'Bearer 14227~78YOvVdyFWPnz01zluLyFYIKJnlQwhdgnBWfCgirn2rGOoVgx0DzLTkBv9YBiUfW','Cookie': '_csrf_token=YPNkX5ol1Pu7wMePwWI8ndcRzOzmdtdnVot%2F0efKd2krwCM29nGjo9HypcS2OE%2Fr4Gj%2BqYg3mwoXySapt6lAMQ%3D%3D; _legacy_normandy_session=L_1zHP9tMabTbjsHzUBNUA.phC85ojpMJ0w74UG6ozNCFyccSE1DxpCPCTI3AjBupm31oYbFu_S4OjLbOZtnz_xIHoX9Zh_YBmkSvNUIPV_2S3AUhEbrBxwXFXJ2eHz49B-5DZFdn-Bhb2cjwVFA2Nu.cbtmLguWFL-TIrmRSJB3bLYpPys.YnuYZQ; canvas_session=L_1zHP9tMabTbjsHzUBNUA.phC85ojpMJ0w74UG6ozNCFyccSE1DxpCPCTI3AjBupm31oYbFu_S4OjLbOZtnz_xIHoX9Zh_YBmkSvNUIPV_2S3AUhEbrBxwXFXJ2eHz49B-5DZFdn-Bhb2cjwVFA2Nu.cbtmLguWFL-TIrmRSJB3bLYpPys.YnuYZQ; log_session_id=f73dcdfdd2c65398a60cd2352060388a'}

        response = requests.request("GET", url, headers=headers, data=payload)
        data = response.json()
        op = []
        for i in data:
            dic = {}
            dic['user_id'] = i['user_id']
            dic['current_grade'] = i["grades"]['current_grade']
            dic['current_score'] = i["grades"]['current_score']
            op.append(dic)
        with open(f+'\\'+str(s)+"final_grade.json", "w+") as jsonFile:
                jsonFile.write(json.dumps(op, indent = 4))
        print('finish')
    return


# assignment grades
def assignmentGrades(subjects, student_lists, f):
    for s in subjects:
        for id in student_lists[s]:
            url = f"https://unimelb-prod.instructure.com/api/v1/courses/{s}/analytics/users/{id}/assignments?per_page=10000"
            payload={}
            headers = {'Authorization': 'Bearer 14227~78YOvVdyFWPnz01zluLyFYIKJnlQwhdgnBWfCgirn2rGOoVgx0DzLTkBv9YBiUfW','Cookie': '_csrf_token=YPNkX5ol1Pu7wMePwWI8ndcRzOzmdtdnVot%2F0efKd2krwCM29nGjo9HypcS2OE%2Fr4Gj%2BqYg3mwoXySapt6lAMQ%3D%3D; _legacy_normandy_session=L_1zHP9tMabTbjsHzUBNUA.phC85ojpMJ0w74UG6ozNCFyccSE1DxpCPCTI3AjBupm31oYbFu_S4OjLbOZtnz_xIHoX9Zh_YBmkSvNUIPV_2S3AUhEbrBxwXFXJ2eHz49B-5DZFdn-Bhb2cjwVFA2Nu.cbtmLguWFL-TIrmRSJB3bLYpPys.YnuYZQ; canvas_session=L_1zHP9tMabTbjsHzUBNUA.phC85ojpMJ0w74UG6ozNCFyccSE1DxpCPCTI3AjBupm31oYbFu_S4OjLbOZtnz_xIHoX9Zh_YBmkSvNUIPV_2S3AUhEbrBxwXFXJ2eHz49B-5DZFdn-Bhb2cjwVFA2Nu.cbtmLguWFL-TIrmRSJB3bLYpPys.YnuYZQ; log_session_id=f73dcdfdd2c65398a60cd2352060388a'}

            response = requests.request("GET", url, headers=headers, data=payload)
            data = response.json()
            with open(f+'\\'+str(s)+'\\'+str(id)+"assignment_grade.json", "w+") as jsonFile:
                jsonFile.write(json.dumps(data, indent = 4))
        print('finish')
    return



# modules items
def modules(subjects, f):
    for s in subjects:
        url = f"https://unimelb-prod.instructure.com/api/v1/courses/{s}/modules?per_page=10000"
        payload={}
        headers = {'Authorization': 'Bearer 14227~78YOvVdyFWPnz01zluLyFYIKJnlQwhdgnBWfCgirn2rGOoVgx0DzLTkBv9YBiUfW','Cookie': '_csrf_token=YPNkX5ol1Pu7wMePwWI8ndcRzOzmdtdnVot%2F0efKd2krwCM29nGjo9HypcS2OE%2Fr4Gj%2BqYg3mwoXySapt6lAMQ%3D%3D; _legacy_normandy_session=L_1zHP9tMabTbjsHzUBNUA.phC85ojpMJ0w74UG6ozNCFyccSE1DxpCPCTI3AjBupm31oYbFu_S4OjLbOZtnz_xIHoX9Zh_YBmkSvNUIPV_2S3AUhEbrBxwXFXJ2eHz49B-5DZFdn-Bhb2cjwVFA2Nu.cbtmLguWFL-TIrmRSJB3bLYpPys.YnuYZQ; canvas_session=L_1zHP9tMabTbjsHzUBNUA.phC85ojpMJ0w74UG6ozNCFyccSE1DxpCPCTI3AjBupm31oYbFu_S4OjLbOZtnz_xIHoX9Zh_YBmkSvNUIPV_2S3AUhEbrBxwXFXJ2eHz49B-5DZFdn-Bhb2cjwVFA2Nu.cbtmLguWFL-TIrmRSJB3bLYpPys.YnuYZQ; log_session_id=f73dcdfdd2c65398a60cd2352060388a'}

        response = requests.request("GET", url, headers=headers, data=payload)
        data = response.json()
        with open(f+'\\'+str(s)+"modeules.json", "w+") as jsonFile:
            jsonFile.write(json.dumps(data, indent = 4))
            print('finish')
    return


# discussion topics
def discussions(subjects, f):
    for s in subjects:
        url = f"https://unimelb-prod.instructure.com/api/v1/courses/{s}/discussion_topics?per_page=10000"
        payload={}
        headers = {'Authorization': 'Bearer 14227~78YOvVdyFWPnz01zluLyFYIKJnlQwhdgnBWfCgirn2rGOoVgx0DzLTkBv9YBiUfW','Cookie': '_csrf_token=YPNkX5ol1Pu7wMePwWI8ndcRzOzmdtdnVot%2F0efKd2krwCM29nGjo9HypcS2OE%2Fr4Gj%2BqYg3mwoXySapt6lAMQ%3D%3D; _legacy_normandy_session=L_1zHP9tMabTbjsHzUBNUA.phC85ojpMJ0w74UG6ozNCFyccSE1DxpCPCTI3AjBupm31oYbFu_S4OjLbOZtnz_xIHoX9Zh_YBmkSvNUIPV_2S3AUhEbrBxwXFXJ2eHz49B-5DZFdn-Bhb2cjwVFA2Nu.cbtmLguWFL-TIrmRSJB3bLYpPys.YnuYZQ; canvas_session=L_1zHP9tMabTbjsHzUBNUA.phC85ojpMJ0w74UG6ozNCFyccSE1DxpCPCTI3AjBupm31oYbFu_S4OjLbOZtnz_xIHoX9Zh_YBmkSvNUIPV_2S3AUhEbrBxwXFXJ2eHz49B-5DZFdn-Bhb2cjwVFA2Nu.cbtmLguWFL-TIrmRSJB3bLYpPys.YnuYZQ; log_session_id=f73dcdfdd2c65398a60cd2352060388a'}

        response = requests.request("GET", url, headers=headers, data=payload)
        data = response.json()
        with open(f+'\\'+str(s)+"discussion_lists.json", "w+") as jsonFile:
            jsonFile.write(json.dumps(data, indent = 4))
            print('finish')
    return


# assignments
def assignments(subjects, f):
    for s in subjects:
        url = f"https://unimelb-prod.instructure.com/api/v1/courses/{s}/assignments?per_page=10000"
        payload={}
        headers = {'Authorization': 'Bearer 14227~78YOvVdyFWPnz01zluLyFYIKJnlQwhdgnBWfCgirn2rGOoVgx0DzLTkBv9YBiUfW','Cookie': '_csrf_token=YPNkX5ol1Pu7wMePwWI8ndcRzOzmdtdnVot%2F0efKd2krwCM29nGjo9HypcS2OE%2Fr4Gj%2BqYg3mwoXySapt6lAMQ%3D%3D; _legacy_normandy_session=L_1zHP9tMabTbjsHzUBNUA.phC85ojpMJ0w74UG6ozNCFyccSE1DxpCPCTI3AjBupm31oYbFu_S4OjLbOZtnz_xIHoX9Zh_YBmkSvNUIPV_2S3AUhEbrBxwXFXJ2eHz49B-5DZFdn-Bhb2cjwVFA2Nu.cbtmLguWFL-TIrmRSJB3bLYpPys.YnuYZQ; canvas_session=L_1zHP9tMabTbjsHzUBNUA.phC85ojpMJ0w74UG6ozNCFyccSE1DxpCPCTI3AjBupm31oYbFu_S4OjLbOZtnz_xIHoX9Zh_YBmkSvNUIPV_2S3AUhEbrBxwXFXJ2eHz49B-5DZFdn-Bhb2cjwVFA2Nu.cbtmLguWFL-TIrmRSJB3bLYpPys.YnuYZQ; log_session_id=f73dcdfdd2c65398a60cd2352060388a'}

        response = requests.request("GET", url, headers=headers, data=payload)
        data = response.json()
        with open(f+'\\'+str(s)+"assignmnets.json", "w+") as jsonFile:
            jsonFile.write(json.dumps(data, indent = 4))
            print('finish')
    return



# quizzes
def quizzes(subjects, f):
    for s in subjects:
        url = f"https://unimelb-prod.instructure.com/api/v1/courses/{s}/quizzes?per_page=10000"
        payload={}
        headers = {'Authorization': 'Bearer 14227~78YOvVdyFWPnz01zluLyFYIKJnlQwhdgnBWfCgirn2rGOoVgx0DzLTkBv9YBiUfW','Cookie': '_csrf_token=YPNkX5ol1Pu7wMePwWI8ndcRzOzmdtdnVot%2F0efKd2krwCM29nGjo9HypcS2OE%2Fr4Gj%2BqYg3mwoXySapt6lAMQ%3D%3D; _legacy_normandy_session=L_1zHP9tMabTbjsHzUBNUA.phC85ojpMJ0w74UG6ozNCFyccSE1DxpCPCTI3AjBupm31oYbFu_S4OjLbOZtnz_xIHoX9Zh_YBmkSvNUIPV_2S3AUhEbrBxwXFXJ2eHz49B-5DZFdn-Bhb2cjwVFA2Nu.cbtmLguWFL-TIrmRSJB3bLYpPys.YnuYZQ; canvas_session=L_1zHP9tMabTbjsHzUBNUA.phC85ojpMJ0w74UG6ozNCFyccSE1DxpCPCTI3AjBupm31oYbFu_S4OjLbOZtnz_xIHoX9Zh_YBmkSvNUIPV_2S3AUhEbrBxwXFXJ2eHz49B-5DZFdn-Bhb2cjwVFA2Nu.cbtmLguWFL-TIrmRSJB3bLYpPys.YnuYZQ; log_session_id=f73dcdfdd2c65398a60cd2352060388a'}

        response = requests.request("GET", url, headers=headers, data=payload)
        data = response.json()
        with open(f+'\\'+str(s)+"quizzes.json", "w+") as jsonFile:
            jsonFile.write(json.dumps(data, indent = 4))
            print('finish')
    return


# files uploaded in subject LMS
def file_lists(subjects, f):
    for s in subjects:
        url = f"https://unimelb-prod.instructure.com/api/v1/courses/{s}/files?per_page=10000"
        payload={}
        headers = {'Authorization': 'Bearer 14227~78YOvVdyFWPnz01zluLyFYIKJnlQwhdgnBWfCgirn2rGOoVgx0DzLTkBv9YBiUfW','Cookie': '_csrf_token=YPNkX5ol1Pu7wMePwWI8ndcRzOzmdtdnVot%2F0efKd2krwCM29nGjo9HypcS2OE%2Fr4Gj%2BqYg3mwoXySapt6lAMQ%3D%3D; _legacy_normandy_session=L_1zHP9tMabTbjsHzUBNUA.phC85ojpMJ0w74UG6ozNCFyccSE1DxpCPCTI3AjBupm31oYbFu_S4OjLbOZtnz_xIHoX9Zh_YBmkSvNUIPV_2S3AUhEbrBxwXFXJ2eHz49B-5DZFdn-Bhb2cjwVFA2Nu.cbtmLguWFL-TIrmRSJB3bLYpPys.YnuYZQ; canvas_session=L_1zHP9tMabTbjsHzUBNUA.phC85ojpMJ0w74UG6ozNCFyccSE1DxpCPCTI3AjBupm31oYbFu_S4OjLbOZtnz_xIHoX9Zh_YBmkSvNUIPV_2S3AUhEbrBxwXFXJ2eHz49B-5DZFdn-Bhb2cjwVFA2Nu.cbtmLguWFL-TIrmRSJB3bLYpPys.YnuYZQ; log_session_id=f73dcdfdd2c65398a60cd2352060388a'}

        response = requests.request("GET", url, headers=headers, data=payload)
        data = response.json()
        with open(f+'\\'+str(s)+"fileLists.json", "w+") as jsonFile:
            jsonFile.write(json.dumps(data, indent = 4))
            print('finish')
    return


# quiz submission
def quiz_submission(id, pages):
    import time
    start = time.time()

    url = f"https://unimelb-prod.instructure.com/api/v1/users/{id}/page_views?per_page=10000"
    payload={}
    headers = {'Authorization': 'Bearer 14227~78YOvVdyFWPnz01zluLyFYIKJnlQwhdgnBWfCgirn2rGOoVgx0DzLTkBv9YBiUfW',
               'Cookie': '_csrf_token=PT0bqPvHiWgkSnBM1Fv06YkD%2FUoQR815fqC46Npy1gBaekvYqoHCCk8zOz6uA6Gg2EmqDHV%2FuhYX04vdlgj5SA%3D%3D; _legacy_normandy_session=MJirGCqnevGhMoqyKa5XPw.ziBaUp-KsTpNbr5gqqVZiF7CHRFvfspK-hSclyQq6jq5e0yxJW0H3emoyCdMF4lEe3RMwkNdBbDZh5DEnP8bbX4klJftdFOermu3YlnzAwFIuTLrjgY1l5nQL6xHcjEf.mAwOqefMhCSk9TXRjI4DoIfzzog.YoL5vg; canvas_session=MJirGCqnevGhMoqyKa5XPw.ziBaUp-KsTpNbr5gqqVZiF7CHRFvfspK-hSclyQq6jq5e0yxJW0H3emoyCdMF4lEe3RMwkNdBbDZh5DEnP8bbX4klJftdFOermu3YlnzAwFIuTLrjgY1l5nQL6xHcjEf.mAwOqefMhCSk9TXRjI4DoIfzzog.YoL5vg; log_session_id=5ca235e7d31935b950e0874e3c5b4c35'}

    keepgoing = True
    counter = 0
    res_li = []
    while keepgoing and counter <= pages:
        #  Make the call to the API URL and pass in our custom header.
        r = requests.get(url, headers=headers)

        # Make sure the call worked, and if not, we want to throw an error.
        if r.status_code != 200:
            print("ERROR: Status code returned={} for {} -- Exiting.\n".format(r.status_code, url))
            sys.exit()
        response = requests.request("GET", url, headers=headers, data=payload)
        counter += 1
    #     print(pd.json_normalize(response.json()))
        res_li += response.json()

        linkheader = r.headers['Link']
        # The header has an array of links, separated by commas...
        linklist = linkheader.split(",")
        # Loop through.  We're looking for the "next" link, if there is one...
        nexturl = None
        for linkitem in linklist:
            # Each link item is really two things, the actual URL, and a rel= that tells us what the link is to...
            onelink = linkitem.split(";")

            if "next" in onelink[1]:
                # Get it, strip the first character (a "<") and the last letter (a ">").
                nexturl = onelink[0]
                nexturl = nexturl[1:]
                nexturl = nexturl[:-1]

        # Now, if the nexturl is blank, set the keepgoing flag to false so we'll drop out of the loop.
        # Otherwise, set url to nexturl and we'll get the next page worth.
        if nexturl:
            url = nexturl
        else:
            keepgoing = False

    df = pd.DataFrame(res_li)
    df.to_csv(f'A_B_C/Student_{id}_pageviews.csv', index=False)

    end = time.time()
    return df, end-start
