import pandas as pd
import json
import re



def read_df(df_name):
    df = pd.read_excel(df_name)
    return df

## read in the pageview dataframe
def read_basic_df(df_name, start, end, subject_id):
    df = read_df(df_name)
    df = df[(df['created_at'] >= start) & (df['created_at'] <= end)]

    df1 = pd.DataFrame()
    df2 = df.copy()
    subset = ['account_notifications', 'calendar_events_api', 'account_notifications', 'accounts', 'announcements',
              'canvadoc_sessions', 'context_module_items_api',
              'conferences', 'custom_data', 'wiki_pages_api', 'tabs', 'search', 'profile', 'lti/lti_apps',
              'lti/ims/authentication',
              'assignment_groups', 'enrollments_api', 'context', 'context_modules', 'context_modules_api',
              'feature_flags', 'users', 'assignments_api', 'discussion_topics_api', 'groups',
              'grading_periods',
              'quizzes/quizzes_api', 'submissions_api', 'quizzes/quizzes', 'file_previews']
    df2 = df2[~(df2['controller'].isin(subset))]
    df1['url'] = df2['url']
    df1['controller'] = df2['controller']
    df1['date'] = df2['created_at'].str.slice(0, 10)
    df1['datetime'] = df2['created_at']
    df1['course_id'] = df1['url'].str.extract('courses/(\d+)')
    df1 = df1[df1['course_id'] == subject_id]

    return df1


# read in assignment
def read_ass(file):
    ass = pd.DataFrame(open_json(file))[['id', 'name', 'unlock_at', 'due_at']]

    ass['unlock_at'] = ass['unlock_at'].str.slice(0, 10)
    ass['due_at'] = ass['due_at'].str.slice(0, 10)
    return ass

def read_ass_grade(file):
    js = open_json(file)
    if 'errors' in js:
        return None
    ass_grade_df = pd.DataFrame(js)[
        ['assignment_id', 'max_score', 'min_score', 'first_quartile', 'median', 'third_quartile', 'submission']]
    return ass_grade_df


"""pageview"""
# def read_quiz_df(df1):
#     df_quiz = df1[df1['controller'] == 'quizzes/quiz_submissions_api']
#     df_quiz['course'] = df_quiz['url'].str.split('/', 10).str[6]
#     df_quiz['quiz'] = df_quiz['url'].str.split('/', 10).str[8]
#     return df_quiz.groupby(['course', 'quiz', 'date']).count()


def read_submission_df(df1):
    # submission
    df_ass = df1[df1['controller'] == 'submissions']
    df_ass['course'] = df_ass['url'].str.split('/', 10).str[4]
    df_ass['ass'] = df_ass['url'].str.split('/', 10).str[6]
    # # submission download
    # df_ass_down = df1[df1['controller'] == 'submissions/downloads']
    # df_ass_down['course'] = df_ass_down['url'].str.split('/', 10).str[4]
    # df_ass_down['ass'] = df_ass_down['url'].str.split('/', 10).str[6]
    # df_assi_down = df_ass.merge(df_ass_down, on=['date', 'course', 'ass'], how='left')
    # # submission preview
    # df_ass_preview = df1[df1['controller'] == 'submissions/previews']
    # df_ass_preview['course'] = df_ass_preview['url'].str.split('/', 10).str[4]
    # df_ass_preview['ass'] = df_ass_preview['url'].str.split('/', 10).str[6]
    # df_ass_dow_pre = df_assi_down.merge(df_ass_preview, on=['date', 'course', 'ass'], how='left')

    return df_ass
    # return df_ass_dow_pre.groupby(['course', 'ass', 'date']).count()


def read_file_df(df1):
    df_file = df1[df1['controller'] == 'files']
    df_file['type'] = None
    df_file['download'] = 0
    df_file['courses_or_ass_id'] = None
    df_file['files_id'] = None
    df_file.loc[df_file['url'].str.contains('download'), 'download'] = 1
    df_file.loc[df_file['url'].str.contains('course'), 'type'] = 'course'
    df_file.loc[df_file['url'].str.contains('assessment_questions'), 'type'] = 'assessments'

    for i in range(len(df_file)):
        line = df_file.iloc[i, 0]
        c_id = re.search('courses/(\d+)', line)
        f_id = re.search('files/(\d+)', line)
        a_id = re.search('questions/(\d+)', line)

        if c_id:
            df_file.iloc[i, 5] = c_id.group(1)
        elif a_id:
            df_file.iloc[i, 5] = a_id.group(1)
        if f_id:
            df_file.iloc[i, 6] = f_id.group(1)

    return df_file.groupby(['type', 'download', 'courses_or_ass_id', 'files_id', 'date']).count()


def read_lec_cap_df(df1):
    return df1[df1['url'].str.contains('external_tools/701')]


def read_mod_df(df1):
    df_mod = df1[df1['url'].str.contains('module_item_id')]

    df_mod['type'] = None
    df_mod['course_id'] = None
    df_mod['mod_id'] = None
    df_mod['file_or_ass_id'] = None
    df_mod.loc[df_mod['url'].str.contains('assignments'), 'type'] = 'assignments'
    df_mod.loc[df_mod['url'].str.contains('pages'), 'type'] = 'pages'
    df_mod.loc[df_mod['url'].str.contains('files'), 'type'] = 'files'

    # df_mod
    for i in range(len(df_mod)):
        line = df_mod.iloc[i, 0]
        c_id = re.search('courses/(\d+)', line)
        m_id = re.search('module_item_id=(\d+)', line)
        f_id = re.search('files/(\d+)', line)
        a_id = re.search('assignments/(\d+)', line)

        if c_id:
            df_mod.iloc[i, -4] = c_id.group(1)
        if m_id:
            df_mod.iloc[i, -2] = m_id.group(1)
        if f_id:
            df_mod.iloc[i, -1] = f_id.group(1)
        elif a_id:
            df_mod.iloc[i, -1] = a_id.group(1)

    return df_mod


def read_ass_df(df1):
    df_as = df1[df1['controller'] == 'assignments']
    df_as['course_id'] = None
    df_as['ass_id'] = None
    for i in range(len(df_as)):
        line = df_as.iloc[i, 0]
        c_id = re.search('courses/(\d+)', line)
        a_id = re.search('assignments/(\d+)', line)

        if c_id:
            df_as.iloc[i, -2] = c_id.group(1)
        if a_id:
            df_as.iloc[i, -1] = a_id.group(1)

    # df_as_group = df_as.groupby(['course_id', 'ass_id', 'date'], dropna=False)
    return df_as


def read_dis_df(df1):
    return df1[(df1['controller']=='discussion_topics')]


def open_json(file):
    f = open(file)
    data = json.load(f)
    f.close()

    return data
