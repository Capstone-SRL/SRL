from study_week import study_information
from read_data import read_df, read_basic_df, read_ass_df, read_dis_df, read_lec_cap_df, read_file_df, read_mod_df, read_submission_df, read_ass, read_ass_grade
import datetime
import pandas as pd


def final_grade(student_id, subject_id):
    # study period information
    study_info = get_study_information(subject_id)
    study_week = study_info['study_week']
    assignment_id = study_info['assignment_id']
    assessment_id = study_info['assessment_id']
    start = study_info['start']
    end = study_info['end']
    exam_period = study_week['w12'][1]

    # assignment df
    ass_info = read_ass(f'Data/assignments/{subject_id}assignments.json')
    ass_grade_df = read_ass_grade(f'Data/assignment_grades/{subject_id}/{student_id}assignment_grade.json')

    # pageview df
    df_name = f'Data/pageview/{subject_id}/student_{student_id}_pageviews.xlsx'
    df = read_df(df_name)
    df1 = read_basic_df(df_name, start, end, subject_id)
    df_ass = read_ass_df(df1)
    df_mod = read_mod_df(df1)
    df_dis = read_dis_df(df1)
    df_lec_cap = read_lec_cap_df(df1)

    df_ass_submission = read_submission_df(df1)

    c1 = cal_c1grade(df_ass, df_mod, df_dis, study_week)
    c2 = cal_c2grade(df, ass_info, assignment_id, study_week)
    c3 = cal_c3grade(df_ass, assignment_id)
    c4 = cal_c4grade(ass_info, df_ass, df_ass_submission, assessment_id)
    c5 = cal_c5grade(df, df_lec_cap, df_mod, df_dis, study_week)
    c7 = cal_c7grade(df_ass, ass_info, assignment_id)
    discussion = dis_activity(df_dis, study_week)
    grade = grade_activity(df1, ass_info)
    ass = ass_activity(df_ass, df_ass_submission, ass_grade_df, ass_info, assignment_id)
    lec = lecture_capture_activity(df_lec_cap, study_week)
    exam = exam_activity(df_dis, df_lec_cap, df_mod, exam_period)

    return {**c1, **c2, **c3, **c4, **c5, **c7, **discussion, **ass, **grade, **lec, **exam}


def get_study_information(subject):
    return study_information[subject]

"""marking function criteria"""
# c1: if check the assignment, module, discussion board in the first four weeks
def cal_c1grade(df_ass, df_mod, df_dis, study_week):
    c1_ass_view = 0
    c1_mod_view = 0
    c1_dis_view = 0
    if sum(df_ass['date'] <= study_week['w4'][1]) > 0:
        c1_ass_view = 1
    if sum(df_mod['date'] <= study_week['w4'][1]) > 0:
        c1_mod_view = 1
    if sum(df_dis['date'] <= study_week['w4'][1]) > 0:
        c1_dis_view = 1
    c1_grade = c1_dis_view + c1_mod_view + c1_ass_view

    res = {'c1_ass_view': c1_ass_view,  # if check the assignment
           'c1_mod_view': c1_mod_view,  # if check the module
           'c1_dis_view': c1_dis_view,  # if check the discussion board
           'c1': c1_grade,                    # if check all of them
           }
    return res

# c2: if the student checks canvas evenly across the semester, having regular long/short study session for both
# normal & lead up day type
def cal_c2grade(df, ass_info, assignment_id, study_week):
    normal_short, normal_long, average_normal_session_duration, average_normal_session_times = cal_normal_session(df, study_week)
    leadup_short, leadup_long, average_leadup_session_duration, average_leadup_session_times \
        = cal_leadup_session(df, ass_info, assignment_id)

    if normal_long > 0 and leadup_long > 0:
        c2_grade = 3
    elif (normal_short > 0 and leadup_long > 0) or (normal_long > 0 and leadup_short > 0):
        c2_grade = 2
    elif leadup_short > 0:
        c2_grade = 1
    else:
        c2_grade = 0

    res = {'normal_short': normal_short,                                # num of weeks with short normal session
           'normal_long': normal_long,                                  # num of weeks with long normal session
           'average_session_duration': average_normal_session_duration, # average session duration for each normal study week
           'average_session_times': average_normal_session_times,       # average times of session visits per day for each normal study week
           'leadup_short': leadup_short,                                # num of weeks with short leadup session
           'leadup_long': leadup_long,                                  # num of weeks with long leadup session
           'average_leadup_session_duration': average_leadup_session_duration, # average session duration for each leadup study week
           'average_leadup_session_times': average_leadup_session_times,# average times of session visits per day for each leadup study week
           'c2': c2_grade,
            }
    return res


# c3: if the student reviews assessment instructions multiple times across the semester
def cal_c3grade(df_ass, assignment_id):
    read_twice = 0
    read_once = 0
    no_read = 0
    df_ass['ass_id'] = df_ass['ass_id'].astype(str)
    for i in assignment_id:
        read_ass = len(df_ass[df_ass['ass_id'] == i])
        if read_ass >= 2:
            read_twice += 1
        elif read_ass >= 1:
            read_once += 1
        else:
            no_read += 1
    if no_read != 0:
        c3_grade = 0
    elif read_once != 0:
        c3_grade = 1
    else:
        c3_grade = 2
    return {'c3_grade': c3_grade}


# c4: if the student completes and reviews extra assessment in the course
def cal_c4grade(ass_info, df_ass, df_ass_submission, assessment_id):
    ass_info['id'] = ass_info['id'].astype(str)
    df_ass['ass_id'] = df_ass['ass_id'].astype(str)
    df_ass_submission['ass'] = df_ass_submission['ass'].astype(str)

    if not assessment_id:
        return {'c4_grade': 3}

    view_before = False
    view_after = False
    complete = False
    for i in assessment_id:
        end = ass_info.loc[ass_info['id'] == i, 'due_at'].values[0]
        if view_after == False:
            view_after = len(df_ass[df_ass['ass_id'] == i]) > 0
        if view_before == False:
            view_before = len(df_ass[(df_ass['ass_id'] == i) & (df_ass['date'] <= end)]) > 0
        if complete == False:
            complete = len(df_ass_submission[df_ass_submission['ass'] == i]) > 0
        if complete and view_after and view_before:
            return {'c4_grade': 3}
    if view_before and complete:
        return {'c4_grade': 2}
    if view_before:
        return {'c4_grade': 1}
    return {'c4_grade': 0}


# Examine information from multiple sources in each session
def cal_c5grade(df, df_lec_cap, df_mod, df_dis, study_week):
    duration_df = session_duration(df)
    duration_df[['start', 'end']] = duration_df[['start', 'end']].astype(str)
    df_lec_cap['datetime'] = df_lec_cap['datetime'].astype(str)
    df_mod['datetime'] = df_mod['datetime'].astype(str)
    df_dis['datetime'] = df_dis['datetime'].astype(str)

    # session
    num_session = len(duration_df)
    num_source = 0

    for i in range(len(duration_df)):
        start = duration_df.iloc[i, 0]
        end = duration_df.iloc[i, 1]

        res = activity_exist(df_lec_cap, start, end) + activity_exist(df_dis, start, end) + activity_exist(df_mod,
                                                                                                           start, end)
        if res == 0:
            num_session -= 1
        num_source += res
    if num_session == 0:
        session = 0
    else:
        session = num_source / num_session

    # week
    num_source = 0
    week = {}

    for i in study_week:
        start = study_week[i][0]
        end = study_week[i][1]
        res = activity_exist(df_lec_cap, start, end) + activity_exist(df_dis, start, end) + activity_exist(df_mod,
                                                                                                           start, end)
        week[i] = res

    # c5grade
    if session >= 2:
        grade = 2
    elif session >= 1:
        grade = 1
    else:
        grade = 0

    return {'source_visit_session': session,            # average num of sources are visited in each session
            'source_visit_week': week,                  # num of sources are visited in each study week
            'c5grade': grade
            }

# c7: the amount of the feedback of assignment a student check for
def cal_c7grade(df_ass, ass_info, assignment_id):
    ass_info['id'] = ass_info['id'].astype(str)
    df_ass['ass_id'] = df_ass['ass_id'].astype(str)
    check_feedback = 0

    for i in assignment_id:
        due = ass_info.loc[ass_info['id'] == i, 'due_at'].values[0]
        check_feedback += (len(df_ass[(df_ass['ass_id'] == i) & (df_ass['date'] > due)]) > 0)

    ratio = check_feedback / len(assignment_id)
    if ratio >= 0.75:
        res = 3
    elif ratio >= 0.5:
        res = 2
    elif ratio >= 0.25:
        res = 1
    else:
        res = 0
    return {'c7_grade': res}


"""Assignment, discussion board, module activity during study week"""
# discussion board
def dis_activity(df_dis, study_week):
    # if check discussion board timely (everyweek)
    check = 0
    for i in study_week:
        start = study_week[i][0]
        end = study_week[i][1]

        check += len(df_dis[(df_dis['date'] >= start) & (df_dis['date'] <= end)]) > 0

    # average times of checking discussion board per week
    average_check = len(df_dis[(df_dis['date'] >= study_week['w1'][0]) & (df_dis['date'] <= study_week['w12'][1])]) / 12

    res = {'check_dis': check,                  # how many weeks does the student check discussion board
           'average_check_dis': average_check   # average times of checking discussion board per week
           }
    return res


def grade_activity(df1, ass_info):
    check_grade = len(df1[df1['controller']=='gradebooks'])/len(ass_info)
    # the average times of a student checking the grade for each assignment
    return {'check_grade': check_grade}


def ass_activity(df_ass, df_ass_submission, ass_grade_df, ass_info, assignment_id):
    ass_info['id'] = ass_info['id'].astype(str)
    df_ass_submission['ass'] = df_ass_submission['ass'].astype(str)
    df_ass['ass_id'] = df_ass['ass_id'].astype(str)

    when_submit = {}
    levels = {}
    check_feedbacks = {}

    for i in assignment_id:
        # when submit
        due = ass_info.loc[ass_info['id'] == i, 'due_at'].values[0]
        due_3 = (strtodate(due) - datetime.timedelta(days=3)).strftime("%Y-%m-%d")
        last_sub = df_ass_submission[df_ass_submission['ass'] == i]
        if ass_grade_df is not None:
            ass_grade_df['assignment_id'] = ass_grade_df['assignment_id'].astype(str)

        # the student doesn't submit the assignment
        if len(last_sub) == 0:
            when_submit[i] = 'absent'

        last_sub_before_due = last_sub[last_sub['date'] <= due]
        last_sub_after_due = last_sub[last_sub['date'] > due]

        # the student submit ass before due
        if len(last_sub_before_due) != 0:
            sub_date = last_sub_before_due['date'].sort_values().values[-1]
            if due_3 < sub_date:
                when_submit[i] = 'after'
            else:
                when_submit[i] = 'before'
        else:
            # the student submit ass after due
            when_submit[i] = 'late'

        # whether the student check the feedback
        check = df_ass[(df_ass['ass_id'] == i) & (df_ass['date'] > due)]
        if len(last_sub_after_due) != 0 or len(check) != 0:
            check_feedback = 1
        else:
            check_feedback = 0
        check_feedbacks[i] = check_feedback

        # ass grade
        if ass_grade_df is not None:
            select = list(ass_grade_df[ass_grade_df['assignment_id'] == i].values)
            if select:
                grade_li = select[0]
                sub = grade_li[-1]
                grade = sub['score']
                maxi = grade_li[1]
                mini = grade_li[2]
                quan1 = grade_li[3]
                quan2 = grade_li[4]
                quan3 = grade_li[5]

                if not grade:
                    level = 0
                elif mini <= grade and grade < quan1:
                    level = 1
                elif quan1 <= grade and grade < quan2:
                    level = 2
                elif quan2 <= grade and grade < quan3:
                    level = 3
                elif quan3 <= grade and grade <= maxi:
                    level = 4
        else:
            level = -1
        levels[i] = level
    return {'when_submit_ass': when_submit,  # when each assignment be submitted, before / in 3 days before due
            'ass_grade_level': levels,  # the grade level compared to the quantile
            'check_feedback': check_feedbacks  # whether the student check the feedback of each assignment
            }


def lecture_capture_activity(df_lec_cap, study_week):
    lec_cap = {}
    df_lec_cap['date'] = df_lec_cap['date'].astype(str)
    for i in study_week.keys():
        start = study_week[i][0]
        end = study_week[i][1]

        lec_cap[i] = len(df_lec_cap[(df_lec_cap['date'] >= start) & (df_lec_cap['date'] <= end)])
    return {'lecture_capture': lec_cap}


"""Exam Activity"""
def exam_activity(df_dis, df_lec_cap, df_mod, exam_period):
    df_dis['date'] = df_dis['date'].astype(str)
    df_lec_cap['date'] = df_lec_cap['date'].astype(str)

    # check discussion board
    dis_time = len(df_dis[df_dis['date'] >= exam_period])
    # check lecture capture
    lec_time = len(df_lec_cap[df_lec_cap['date'] >= exam_period])
    # check module
    mod_time = len(df_mod[df_mod['date'] >= exam_period])

    return {'check_discussion': dis_time,
            'check_lecture_capture': lec_time,
            'check_module': mod_time}




######################################################
"""c2 criteria"""
# transfer string datetime to datetime type
def strtodatetime(dt):
    return datetime.datetime.strptime(dt, "%Y-%m-%dT%H:%M:%SZ")


# transfer string date to datetime type
def strtodate(dt):
    return datetime.datetime.strptime(dt, "%Y-%m-%d")


# check if the time stamp interval is larger than 30 mins
def check_session(start, end):
    return (strtodatetime(end) - strtodatetime(start) > datetime.timedelta(minutes=30))


# get the start and end time of each session and its duration
def session_duration(df):
    session_li = list(df['created_at'].sort_values())
    duration_li = []

    start = session_li[0]
    for i in range(len(session_li) - 1):
        if check_session(session_li[i], session_li[i + 1]) == True:
            end = session_li[i]
            duration_li.append((start, end, (strtodatetime(end) - strtodatetime(start)).total_seconds()))
            start = session_li[i + 1]
    duration_li.append((start, session_li[-1], (strtodatetime(session_li[-1]) - strtodatetime(start)).total_seconds()))
    duration_df = pd.DataFrame(duration_li, columns=['start', 'end', 'sec'])

    return duration_df

""""c2 -- normal"""
def cal_normal_session(df, study_week):
    duration_df = session_duration(df)
    session_times = pd.DataFrame(df['created_at'].sort_values())

    normal_short = 0
    normal_long = 0
    average_session_duration = {}
    average_session_times = {}

    for i in study_week:
        start = study_week[i][0]
        end = study_week[i][1]

        sec_for_week = duration_df[(duration_df['start'] >= start) & (duration_df['end'] <= end)]['sec']
        average_session_duration[i] = sec_for_week.mean()
        times_for_week = session_times[(session_times['created_at'] >= start) & (session_times['created_at'] <= end)]
        average_session_times[i] = len(times_for_week) / 7

        if sum(sec_for_week >= 50 * 60) > 0:
            normal_short += 1
            normal_long += 1
        elif len(sec_for_week) > 0:
            normal_short += 1
    return normal_short, normal_long, average_session_duration, average_session_times


"""c2 -- leadup"""
def cal_leadup_session(df, ass_df, ass_id):
    duration_df = session_duration(df)
    session_times = pd.DataFrame(df['created_at'].sort_values())
    ass_df['id'] = ass_df['id'].astype(str)

    leadup_short = 0
    leadup_long = 0
    average_session_duration = {}
    average_session_times = {}

    for i in ass_id:
        end = ass_df.loc[ass_df['id'] == i, 'due_at'].values[0]
        start = (strtodate(end) - datetime.timedelta(days=3)).strftime("%Y-%m-%d")

        sec_for_lead_up = duration_df[(duration_df['start'] >= start) & (duration_df['end'] <= end)]['sec']
        average_session_duration[i] = sec_for_lead_up.mean()

        times_for_lead_up = session_times[(session_times['created_at'] >= start) & (session_times['created_at'] <= end)]
        average_session_times[i] = len(times_for_lead_up) / 3

        if sum(sec_for_lead_up >= 50 * 60) > 0:
            leadup_short += 1
            leadup_long += 1
        elif len(sec_for_lead_up) > 0:
            leadup_short += 1

    return leadup_short, leadup_long, average_session_duration, average_session_times


#######################################################
"""c5 criteria"""
def activity_exist(df, start, end):
    res = df[(df['datetime']>=start) & (df['datetime']<=end)]
    return len(res)