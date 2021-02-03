# Example 12*4+7/4# Example 2 - ignore errorsperson = create_person(firstname, surname, age, city, nationality, gender, height, weight)# Example 3def get_lengthy_condition(data): return data is not None and data != "" and len(data) > 3 and len(data) < 20

def get_condition(data):
    if data and  3 < len(data) < 20:
        return True
    return False

print(get_condition([1,2,3]))