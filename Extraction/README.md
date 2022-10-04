This repository contains codes that used to extract raw data from Canvas API and preprocess raw data into marking function scores for each student.


## Extract_data.py
data could be extracted for each subject
#### final grades
#### assignments grades
#### modules of subjects
#### discussion board topics
#### assignments
#### quizzes
#### file lists
data could be extracted for each students
#### pageviews
#### quiz_submission

## study_week.py
predefine the sduty week for each subjects
## read_data.py
read data from raw data files extracted by the above codes
## preprocess.py
process the data again before calculating the marking function scores
##calGrade.py
calculate the scores for each items of marking function (except item6)
####  final_grade
#### cal_c1grade
#### cal_c2grade
#### cal_c3grade
#### cal_c4grade
#### cal_c5grade
#### cal_c7grade
