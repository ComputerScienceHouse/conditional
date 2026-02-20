def user_dict_is_in_group(user_dict, group) -> bool:
    return group in user_dict['groups']

def user_dict_is_active(user_dict) -> bool:
    return user_dict_is_in_group(user_dict, 'active')

def user_dict_is_bad_standing(user_dict) -> bool:
    return user_dict_is_in_group(user_dict, 'bad_standing')

def user_dict_is_alumni(user_dict) -> bool:
    return not user_dict_is_active(user_dict)

def user_dict_is_eboard(user_dict) -> bool:
    return user_dict_is_in_group(user_dict, 'eboard')

def user_dict_is_rtp(user_dict) -> bool:
    return user_dict_is_in_group(user_dict, 'active_rtp')

def user_dict_is_intromember(user_dict) -> bool:
    return user_dict_is_in_group(user_dict, 'intromembers')

def user_dict_is_onfloor(user_dict) -> bool:
    return user_dict_is_in_group(user_dict, 'onfloor')

def user_dict_is_financial_director(user_dict) -> bool:
    return user_dict_is_in_group(user_dict, 'eboard-financial')

def user_dict_is_eval_director(user_dict) -> bool:
    return user_dict_is_in_group(user_dict, 'eboard-evaluations')

def user_dict_is_current_student(user_dict) -> bool:
    return user_dict_is_in_group(user_dict, 'current_student')
