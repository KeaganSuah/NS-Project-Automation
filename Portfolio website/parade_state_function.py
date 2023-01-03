from tinydb import TinyDB, Query
import datetime

# The variables needed when managing and importing the Tiny Database
User = Query()
db = TinyDB('website/db.json')
ps_time_submission = TinyDB('website/time_submission_db.json')

"""DATA STRUCTURES"""
# This dictionary will hold on to all the personnel attendance status
attendance_records = dict()
# This dictionary will be used to collect all the personnel reasons for not being present in the morning
recorded_absences = dict()

# Attendance library for all submitted records
display_attendance = dict()
display_attendance_sort = dict()
# Un-responded data
display_unresponsive_sort = dict()
display_unresponsive = dict()
# stores personnel rank for all branches per status
status_branch = {'Present': {'s1': [], 's2': [], 's3': [], 's4': [], 's5': []}, 'Late': {'s1': [], 's2': [], 's3': [], 's4': [], 's5': []}, 'HLS': {'s1': [], 's2': [], 's3': [], 's4': [], 's5': []}, 'DUTY': {'s1': [], 's2': [], 's3': [], 's4': [], 's5': []}, 'Work From Home': {'s1': [], 's2': [], 's3': [], 's4': [], 's5': []}, 'Outside Stationed': {'s1': [], 's2': [], 's3': [], 's4': [], 's5': []}, 'Attached Out': {'s1': [], 's2': [], 's3': [], 's4': [], 's5': []}, 'On Course': {'s1': [], 's2': [], 's3': [], 's4': [], 's5': []}, 'Day Off': {'s1': [], 's2': [], 's3': [], 's4': [], 's5': []}, 'Local Leave': {'s1': [], 's2': [], 's3': [], 's4': [], 's5': []}, 'Overseas Leave': {'s1': [], 's2': [], 's3': [], 's4': [], 's5': []}, 'Medical Leave': {'s1': [], 's2': [], 's3': [], 's4': [], 's5': []}, 'Medical / Dental appointment': {'s1': [], 's2': [], 's3': [], 's4': [], 's5': []}, 'Report Sick Inside': {'s1': [], 's2': [], 's3': [], 's4': [], 's5': []}, 'Report Sick Outside': {'s1': [], 's2': [], 's3': [], 's4': [], 's5': []}, 'Hospitalised / Sickbay': {'s1': [], 's2': [], 's3': [], 's4': [], 's5': []}, 'AWOL': {'s1': [], 's2': [], 's3': [], 's4': [], 's5': []}, 'OTHERS': {'s1': [], 's2': [], 's3': [], 's4': [], 's5': []}}


# list of different branches for generating Summary for Excel
summary_S1 = dict()
summary_S3 = dict()
summary_S4 = dict()
summary_S5 = dict()
summary_S2 = dict()

summary_library_forExcel = [summary_S1, summary_S2, summary_S3, summary_S4, summary_S5]


# list of different branches for generating Summary for display
summary_S1_display = dict()
summary_S3_display = dict()
summary_S4_display = dict()
summary_S2_display = dict()
summary_S5_display = dict()
summary_library = [summary_S1_display, summary_S3_display, summary_S4_display,  summary_S5_display, summary_S2_display]

# list of different branches for gathering all the names
s1 = []
s3 = []
s4 = []
s2 = []
s5 = []
branches_list = [s1, s2, s3, s4, s5]

# list of branches in string format
branches_string = ['s1', 's2', 's3', 's4', 's5']
# branches formatted for the dropdown list
dropdown_branch = {'s1': 's1 branch', 's2': 's2 branch', 's3': 's3 branch', 's4': 's4 branch', 's5': 's5 branch'}

# types of status and ranking
status = ["Present", "Late", "HLS", "DUTY", "Work From Home", "Outside Stationed", "Attached Out",
          "On Course", "Day Off", "Local Leave",
          "Overseas Leave", "Medical Leave", "Medical / Dental appointment",
          "Report Sick Inside", "Report Sick Outside",
          "Hospitalised / Sickbay", "AWOL", "OTHERS"]
ranking = ['me6', 'me5', 'me4', 'cpt', 'lta', '2lt',
           'dxo', 'me3', 'me2', 'me1', '3sg', 'me4a', 'me1t', 'sct', 'cfc', 'cpl', 'lcp', 'pte', 'rec']

"""DATABASE FUNCTIONS"""


# function to enter details into the database
def insert(rank, name, branch):
    db.insert({'rank': rank, 'name': name, 'branch': branch})


# function to remove a personnel details from the database
def delete_by_name(name):
    db.remove(User.name == name)


# search through the database
def search(var):
    for user in db.all():
        user = user.get('name')
        if var == user:
            return True
        else:
            continue


"""SUBMITTING AND CALCULATING PARADE STATE FUNCTIONS"""


# functions required for displaying, submitting parade state
def submit():
    # clearing all dictionaries needed
    for status_lib, all_branches in status_branch.copy().items():
        status_branch[status_lib] = {'s1': [], 's2': [], 's3': [], 's4': [], 's5': []}
    for summary, summary_display in zip(summary_library_forExcel, summary_library):
        summary.clear()
        summary_display.clear()
    display_attendance.clear()
    display_attendance_sort.clear()
    display_unresponsive_sort.clear()
    display_unresponsive.clear()
    # Function for submitting
    period_submission_generator()
    generate_unresponsive()
    generate_response()
    summary_display_generator()


# manage data that personnel have sent to the website
def generate_response():
    # gathering all data in attendance_record and retrieving other personnel particulars in database
    for name_in_record, status_data in attendance_records.items():
        result = db.search(User.name == name_in_record)
        for match in result:
            # transferring data to dictionary that will be formatted for display 2022-05-10
            display_attendance[str(match.get('name'))] = [str(match.get('rank')), str(match.get('branch')),
                                                          str(status_data[0]), str(status_data[1]),
                                                          str(status_data[2][8:10]) + str(status_data[2][4:7])
                                                          + '-' + str(status_data[2][0:4])]
            # transfer to dictionary for summary
            if status_data[0] == 'HLS' or status_data[0] == 'DUTY' or status_data[0] == 'Late':
                status_branch['Present'][match.get('branch')] += [match.get('rank')]
            else:
                status_branch[str(status_data[0])][match.get('branch')] += [match.get('rank')]
    # sorting and changing personnel positions
    name_convertor(display_attendance, " , ", "'")
    sort(display_attendance_sort, display_attendance, ranking, 0)
    sort(display_attendance, display_attendance_sort, status, 2)
    sort(display_attendance_sort, display_attendance, branches_string, 1)
    for status_data in branches_string:
        final_display(str(status_data).upper())


# final check and getting all necessary attributes
def final_display(branch):
    for name, var in display_attendance_sort.items():
        if str(var[1]).upper() == branch:
            display_attendance[str(name).upper()] = [str(var[0]).upper(),
                                                     str(var[1]).upper(), str(var[2]), str(var[3]), str(var[4])]


# manage data of personnel that did not response
def generate_unresponsive():
    # getting all necessary data from database
    personnel_database = db.all()
    for person in personnel_database:
        found = person.get("name")
        rank = person.get("rank")
        branch = person.get("branch")
        name_convertor(attendance_records, " , ", "'")
        # check if personnel have responded with other dictionary
        if found in attendance_records:
            continue
        else:
            if found in recorded_absences:
                for name, state in recorded_absences.items():
                    if state[0] == 'Present':
                        # send to roll call to be authenticated
                        display_unresponsive_sort[str(found)] = [str(rank), str(branch), str(state[0]),
                                                                 str(state[1]),
                                                                 str(state[2])]
                    else:
                        attendance_records[str(name)] = [str(state[0]), str(state[1]), str(state[2])]
            else:
                # if not found, assume they are present and roll call will authenticate it
                display_unresponsive_sort[str(found)] = [str(rank), str(branch), "Present", "Present", '']
    name_convertor(display_unresponsive_sort, "'", " , ")
    sort(display_unresponsive, display_unresponsive_sort, ranking, 0)


# calculated the total strength and absences
def summary_display_strength_generator(dictionary, total):
    strength = 0
    absent = 0
    item = list(dictionary.keys())
    for word in item[0:1]:
        strength += len(dictionary.get(word))
    for word in item[1:]:
        absent += len(dictionary.get(word))
    total['TOTAL STRENGTH'] = str(strength)
    total['TOTAL ABSENTEES'] = str(absent)


# managing all data per status and placing the total strength and absences
def summary_display_generator():
    for status_library, branch_library in status_branch.items():
        for summary, branch, summary_display in zip(summary_library_forExcel, branches_string, summary_library):
            summary[status_library] = branch_library[branch]
            for state, total in summary.items():
                summary_display[state] = str(len(total))
    for summary, summary_display in zip(summary_library_forExcel, summary_library):
        summary_display_strength_generator(summary, summary_display)


# used to sort display dictionaries according to interest
def sort(sorted_dict, unsorted_dict, ordination, no):
    for i in ordination:
        for items in unsorted_dict.keys():
            if unsorted_dict[items][no] == i:
                sorted_dict[items] = unsorted_dict[items]
    unsorted_dict.clear()


# Generate out the name in the branches from the database
def name_in_branch_generator(variable):
    for branch_var, branch_string in zip(branches_list, branches_string):
        branch_var.clear()
        result = db.search(User.branch == branch_string)
        for personnel in result:
            branch_var.append(personnel[variable])
        branch_var.sort()


# function to enter details into the database
def new_time_submission(name, am_state, pm_state, date):
    ps_time_submission.insert({'name': name, 'am_state': am_state, 'pm_state': pm_state, 'date': date})


# function to remove a personnel details from the database
def remove_submission(name):
    ps_time_submission.remove(User.name == name)


# stores data for personnel that submit status with long periods
recorded_absences_LongPeriod = dict()


# function to manage recorded_absences_LongPeriod dictionary, submit parade state and removing when time is up
def period_submission_generator():
    recorded_absences_LongPeriod.clear()
    for submission in ps_time_submission.all():
        recorded_absences_LongPeriod[submission.get('name')] = [submission.get('am_state'), submission.get('pm_state'),
                                                                submission.get('date')]
    previous = datetime.datetime.today() - datetime.timedelta(days=1)
    SG_time = previous + datetime.timedelta(hours=17)
    formatted = '%Y-%m-%d'
    date = SG_time.strftime(formatted)
    for k, v in recorded_absences_LongPeriod.copy().items():
        if str(v[2]) == str(date):
            remove_submission(k)
        else:
            recorded_absences[k] = [v[0], v[1], v[2]]


# changing particulars of personnel from database
def amended_particulars_generator(input_rank, search_name, input_name):
    db.update({'rank': input_rank}, User.name == search_name)
    if input_name != '':
        db.update({'name': input_name}, User.name == search_name)


# convert names that have inverted colon into comma
def name_convertor(dictionary, old, new):
    for name, attributes in dictionary.copy().items():
        new_name = name.replace(old, new)
        dictionary[new_name] = dictionary.pop(name)


def generate_status_branch():
    branch_dict = dict()
    empty_status_branch = dict()
    for state in status:
        for branch in branches_string:
            branch_dict[branch] = []
        empty_status_branch[state] = branch_dict
    print(empty_status_branch)


branches_uncompleted = []


# to see which branch have not submitted
def generate_branch_not_submitted():
    branches_uncompleted.clear()
    generate_unresponsive()
    sort(display_unresponsive_sort, display_unresponsive, branches_string, 1)
    for name, details in display_unresponsive_sort.copy().items():
        if str(dropdown_branch.get(str(details[1]))) in branches_uncompleted:
            continue
        else:
            branches_uncompleted.append(str(dropdown_branch.get(str(details[1]))))


# testing = dict()
# for state in status:
#     test = dict()
#     for branch in branches_string:
#         test[branch] = []
#     testing[state] = test
# print(testing)
