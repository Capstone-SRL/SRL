# SRL
<add>
how to extract data from postman

<add>
the meaning of each analysis file and the execution way.
### Data extraction, Model training, Prediction and dashborad display

All functions can be achieved by adding parameters when executing `main.py` file.
- Data Strcuture
```
| - SRL
    | - Data: data resource to extract training data set
        | - pageviews: pageview for each student
            | - <subject_id>
                | - student_<student_id>_pageviews.xlsx
        | - assignment_grade: assignment grades for each student
            | - <subject_id>
                | - <student_id>assignment_grades.json
        | - assignments: assignment information for each subject with name <subject_id>assignments.json
        | - discussions: discussion board information for each subject with name <subject_id>discussion_lists.json
        | - fileLists: file information for each subject with name <subject_id>fileLists.json
        | - final_grade: final grades for each suject with name <subject_id>final_grade.json
        | - modules: module information for each subject with name <subject_id>modeules.json
        | - quizzes: quiz information for each subject with name <subject_id>quizzes.json
    | - pkmodel: the storation of all trained model
        | - <model_name>_<data_type>_model.pkl: all models with different data types
        | - best_<model_name>_<data_type>_model.pkl: best model with highest accuracy chosen from all models
```

- Parameter
```
--extract: Data extraction. 
           default = 1, meaning generate training data from `Data` file. The generated data will be stored at 'res.xlsx'. If the user wants to training on new data, please follow the structure and naming rules showed in `Struture`. Else set this parameter to 0, meaning using the existing data file.
--select: Model selection. 
           default = 1, meaning retraining six different models on dataset. All models can be found in 'pkmodel' file.
--predict: Model prediciton. 
           default = 1, meaning make predictions on test data. If `--test` is not set, the prediction would happen on training data. Else it would happen on the given test data.
--test: Test file path for predictions with data type String. 
           default = None.
--display: Generate a dashborad for model analysis and prediction. 
           default = 0, meaning not display.
```

- Execution
```
python main.py (with parameter needed)

# ex: make preditions
python main.py --extract 0 --select 0 --predict 1 --test <test_file>

# ex: dashborad
python main.py --extract 0 --select 0 --predict 0 --display 1
```

Notice: 
1. If the user wants to format a code-available test data, he could add another directory and follow the structure of `Model` directory. Change the value of variable `folder` to test_data_dir & the output excel name in `main.py` file.
2. As we use subject_id as one of the attributes in the model, please make sure the test data are in the same subject as training file, otherwise it could be error.
3. All needed library are shown in requirements.txt
