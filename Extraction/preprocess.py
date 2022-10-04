def unpack(data):
    li = ['average_leadup_session_duration', 'average_leadup_session_times', 'when_submit_ass', 'ass_grade_level', 'check_feedback']

    res = {}
    for i in data:
        ele = data[i]
        if isinstance(ele, dict):
            if i not in li:
                for j in ele:
                    res[f'{i}_{j}'] = ele[j]
            else:
                key = list(ele.keys())
                for j in range(len(key)):
                    res[f'{i}_{j}'] = ele[key[j]]
        else:
            res[i] = ele
    return res