from flask import Blueprint, render_template, request, flash, redirect, url_for, send_file
from parade_state_function import submit, insert, delete_by_name, search, display_attendance, display_unresponsive, \
    status, \
    name_in_branch_generator, branches_list, summary_library_forExcel, summary_library, attendance_records, \
    recorded_absences, new_time_submission, remove_submission, \
    ranking, branches_string, dropdown_branch, generate_branch_not_submitted, branches_uncompleted
from excel_formating import save_file, transfer_attendance_excel, transfer_summary_excel, insert_new_personnel, \
    type_xl_ps, type_xl_summary,\
    clear_excel_range, tracking_delete
from duty_planner_functions import DO_db, DO_FORECAST, duty_insert,\
    excel_to_dictionary, generate_names_list, requested_blockout_do, accepted_blockout, \
    swap_duty, standby_activate, exchange_personnel, exchange_personnel_standby, unavailability_reasons, \
    sign_extra_do, duty_amend_name_depot, generate_blockout_display,\
    empty_do, duty_plan_generator, DO_POINTS, duty_delete_name, submitted_available
from flask_login import current_user
import datetime

views = Blueprint('views', __name__, template_folder='template')


@views.route('/database/add', methods=["GET", "POST"])
def adding_data():
    # current login user only can add personnel to the branch that is authorized for them
    name_in_branch_generator('name')
    if request.method == 'POST':
        # input for all particulars of new personnel
        rank = str(request.form['rank']).lower()
        name = str(request.form['name']).lower()
        name2 = str(request.form['name2']).lower()
        branch = str(request.form['branch']).lower()
        if name != name2:
            flash("Please ensure that the name and the confirmation name are the same.", category='error')
        elif search(name) is True or search(name2) is True:
            flash("Personnel is already inside the database.", category='error')
        elif rank == 'Choose your option' or branch == 'Choose your option':
            flash("Please select from the options provided.", category='error')
        elif '"' in name:
            flash("Please do not use \" in names.", category='error')
        else:
            insert(rank, name, branch)
            # adding personnel into their branch Excel sheet
            for branch_string, worksheet in zip(branches_string, type_xl_ps):
                if branch == branch_string:
                    insert_new_personnel(worksheet, rank.upper(), name.lower())
                    save_file()
            flash("Personnel has been added into the database.", category='success')
            return redirect(url_for('views.adding_data'))
    return render_template("add_database.html", user=current_user, ranking=ranking, branches_string=branches_string,
                           dropdown_branch=dropdown_branch)


@views.route('/database/remove', methods=["GET", "POST"])
def removing_data():
    # current login user only can remove personnel to the branch that is authorized for them
    name_in_branch_generator('name')
    if request.method == 'POST':
        # input for the branch selected
        chosen_branch = str(request.form['removing_branch'])
        for branch_string in branches_string:
            if chosen_branch == branch_string:
                delete_name = str(request.form['delete_name' + branch_string]).lower()
                if search(delete_name) is True:
                    # remove personnel from database and Excel sheet
                    delete_by_name(delete_name)
                    tracking_delete(str(delete_name).lower(), str(chosen_branch))
                    save_file()
                    flash("Personnel has been remove from the database.", category='success')
                    return redirect(url_for('views.removing_data'))
                else:
                    flash("Personnel does not exist in the database.", category='error')
    return render_template("remove_database.html", user=current_user, branches_string=branches_string,
                           zip=zip, branches_list=branches_list,
                           dropdown_branch=dropdown_branch)


# main page for navigating parade state related pages
@views.route('/', methods=["GET", "POST"])
def index():
    displaying_date = (datetime.datetime.today() + datetime.timedelta(hours=17)).strftime('%d/%m/%Y')
    # to see which branch have not submitted
    generate_branch_not_submitted()
    # current login user only can view parade state that is authorized for them
    if request.method == 'POST':
        selected_request = str(request.form['submit_button'])
        # view parade state submitted
        if selected_request == 'parade state':
            return redirect(url_for('views.roll_call'))
        elif selected_request == 'submission':
            return redirect(url_for('views.attendance'))
        # transfer parade state data into Excel file, and export it out
        elif selected_request == 'export':
            submit()
            name_in_branch_generator('rank')
            value = 0
            for sum_xl in type_xl_summary:
                clear_excel_range(sum_xl, 6, 22, 3, 20)
                clear_excel_range(sum_xl, 3, 22, 3, 4)
                transfer_attendance_excel(display_attendance, type_xl_ps[value])
                transfer_summary_excel(summary_library_forExcel[value], branches_list[value], sum_xl)
                save_file()
                value += 1
            return redirect(url_for('views.download_file'))
        elif selected_request == 'remove':
            return redirect(url_for('views.removing_data'))
        elif selected_request == 'add':
            return redirect(url_for('views.adding_data'))
        elif selected_request == 'amend':
            return redirect(url_for('views.amending_data'))
        elif selected_request == 'download':
            return redirect(url_for('views.download_file_database'))
        elif selected_request == 'submission':
            return redirect(url_for('views.download_file_submission'))
        elif selected_request == 'user_database':
            return redirect(url_for('views.download_file_user_database'))
        else:
            flash("Please choose an option", category='error')
    return render_template("home.html", user=current_user, displaying_date=displaying_date,
                           branches_uncompleted=branches_uncompleted)


# page for personnel to submit their reasons for not attending roll call
@views.route('/attendance', methods=["GET", "POST"])
def attendance():
    displaying_date = (datetime.datetime.today() + datetime.timedelta(hours=17)).strftime('%d/%m/%Y')
    time_now = datetime.datetime.now()
    SG_time = time_now + datetime.timedelta(hours=17)
    current_date = SG_time.strftime('%Y-%m-%d')
    current_date = current_date.replace('-', '')
    name_in_branch_generator('name')
    if request.method == 'POST':
        # input for selected branch and period if filled
        chosen_branch = str(request.form['chosen_branch'])
        date = str(request.form['date_sub'])
        # if user submit without choosing branch, flash an error
        if chosen_branch == 'Choose your option':
            flash("Please select the branch you belong", category='error')
        else:
            for branch_string in branches_string:
                if chosen_branch == branch_string:
                    # input for name, AM status and PM status
                    name = str(request.form['name' + branch_string])
                    am = str(request.form['am_' + branch_string])
                    pm = str(request.form['pm_' + branch_string])
                    if name == '* Required *' or am == '* Required *' or pm == '* Required *':
                        flash("Please fill in the required fields", category='error')
                    else:
                        if date != '' and int(date.replace('-', '')) < int(current_date):
                            flash("Please choose a date that is not over", category='error')
                        else:
                            # submit the inputs into the dictionary, recorded absences or recorded absences for long period
                            multiple_branch_reasons(date, name, am, pm)
                            flash('Thank you '+str(name).upper()+' for submitting your status.', category='success')
                            return redirect(url_for('views.index'))
    return render_template('attendance.html', user=current_user, status=status, branches_list=branches_list,
                           branches_string=branches_string, dropdown_branch=dropdown_branch, zip=zip, displaying_date=displaying_date)


# manage data from absences submission page and placing them to the necessary dictionaries
def multiple_branch_reasons(time, name, am, pm):
    time_now = datetime.datetime.now()
    hour_now = time_now.strftime("%H")
    # server and Singapore time is different by 8 hours
    difference_SG_UTC = 8
    acceptable_time = [9, 10, 11, 12, 13, 14]
    if int(hour_now) + difference_SG_UTC in acceptable_time:
        if time == '':
            if pm == 'Choose your option, if necessary':
                pm = am
                remove_submission(name)
                attendance_records[name] = [am, pm, time]
            else:
                remove_submission(name)
                attendance_records[name] = [am, pm, time]
        else:
            if pm == 'Choose your option, if necessary':
                pm = am
                new_time_submission(name, am, pm, time)
            else:
                new_time_submission(name, am, pm, time)
    else:
        if time == '':
            if pm == 'Choose your option, if necessary':
                pm = am
                attendance_records.pop(name, None)
                remove_submission(name)
                recorded_absences[name] = [am, pm, time]
            else:
                attendance_records.pop(name, None)
                remove_submission(name)
                recorded_absences[name] = [am, pm, time]
        else:
            if pm == 'Choose your option, if necessary':
                pm = am
                attendance_records.pop(name, None)
                new_time_submission(name, am, pm, time)
            else:
                attendance_records.pop(name, None)
                new_time_submission(name, am, pm, time)


# Commanders use this page to authenticate the Present status for personnel
@views.route('/roll_call', methods=["GET", "POST"])
def roll_call():
    displaying_date = (datetime.datetime.today() + datetime.timedelta(hours=17)).strftime('%d/%m/%Y')
    # current login user only can manage roll call that is authorized for them
    generate_branch_not_submitted()
    submit()
    if request.method == 'POST':
        submit()
        # only get data from the unresponsive dictionary
        for name, characters in display_unresponsive.copy().items():
            try:
                state_am = request.form[str(name)]
                state_pm = request.form[str(name).upper()]
            except KeyError:
                return redirect(url_for('views.roll_call'))
            if state_am == 'Present':
                attendance_records[name] = [state_am, characters[3], '']
            # when commanders did not fill anything, it will skip the personnel until recorded
            elif state_am == 'Report Sick Inside' or state_am == 'Report Sick Outside':
                attendance_records[name] = [state_am, 'Medical Leave', '']
            elif (state_am != 'AM STATUS' and state_pm == 'PM STATUS') or (state_am == 'AM STATUS' and state_pm != 'PM STATUS'):
                flash("Please fill up both AM and PM for Absentees", category='error')
            elif state_am == 'AM STATUS':
                continue
            else:
                attendance_records[name] = [state_am, state_pm, '']
        for name_recorded, characters_recorded in display_attendance.copy().items():
            try:
                edit_am = request.form["edit_am" + str(name_recorded)]
                edit_pm = request.form["edit_pm" + str(name_recorded)]
            except KeyError:
                return redirect(url_for('views.roll_call'))
            if (edit_am != 'AM STATUS' and edit_pm == 'PM STATUS') or (edit_am == 'AM STATUS' and edit_pm != 'PM STATUS'):
                flash("Please fill up both AM and PM for Absentees", category='error')
            elif edit_am == 'AM STATUS' and edit_pm == 'PM STATUS':
                continue
            else:
                recorded_absences.pop(name_recorded.lower(), None)
                remove_submission(name_recorded.lower())
                attendance_records[name_recorded.lower()] = [edit_am, edit_pm, '']
        return redirect(url_for('views.roll_call'))
    return render_template("rollcall.html", user=current_user, display_unresponsive=display_unresponsive, status=status,
                           display_attendance=display_attendance,
                           branches_string=branches_string, summary_library=summary_library,
                           dropdown_branch=dropdown_branch, zip=zip, displaying_date=displaying_date,
                           branches_uncompleted=branches_uncompleted)


# download Parade state Excel file
@views.route('/download', methods=["GET", "POST"])
def download_file():
    p = "PARADE_STATE.xlsx"
    return send_file(p, as_attachment=True)


@views.route('/duty_submission', methods=["GET", "POST"])
def duty_submission():
    name_list_do = []
    generate_names_list(DO_db, name_list_do)
    unavailable_list = list(unavailability_reasons.keys())
    if request.method == 'POST':
        blockout_do = str(request.form['blockout_do'])
        if blockout_do == 'Choose your option':
            flash("Please select from the options provided.", category='error')
        else:
            requested_blockout_do[blockout_do] = {}
            for blockout_reason in unavailable_list:
                unavailable_dates = str(request.form[str(blockout_reason.upper())])[1:]
                if unavailable_dates == '':
                    continue
                else:
                    requested_blockout_do[blockout_do][str(blockout_reason)] = unavailable_dates
            flash("Your submission was successful, Please consult the Duty Manager to accept your request.", category='success')
            return redirect(url_for('views.duty_home'))
    return render_template("duty_submission.html", user=current_user, name_list_do=name_list_do, unavailable_list=unavailable_list)


@views.route('/duty_submission_available', methods=["GET", "POST"])
def duty_submission_available():
    name_list_do = []
    generate_names_list(DO_db, name_list_do)
    if request.method == 'POST':
        available_dates = str(request.form['available_dates'])
        blockout_do = str(request.form['blockout_do'])
        if blockout_do == 'Choose your option':
            flash("Please select from the options provided.", category='error')
        else:
            submitted_available(DO_db, blockout_do, available_dates)
            flash("Your submission was successful, Please consult the Duty Manager to accept your request.", category='success')
            return redirect(url_for('views.duty_home'))
    return render_template("duty_submission_available.html", user=current_user, name_list_do=name_list_do)


@views.route('/duty_home', methods=["GET", "POST"])
def duty_home():
    if request.method == 'POST':
        choosing_do_doo = str(request.form['duty_main'])
        if choosing_do_doo == 'unavailable':
            return redirect(url_for('views.duty_submission'))
        elif choosing_do_doo == 'available':
            return redirect(url_for('views.duty_submission_available'))
        elif choosing_do_doo == 'submission':
            return redirect(url_for('views.duty_blockout_do'))
        elif choosing_do_doo == 'generate':
            duty_plan_generator(15, 7, DO_db, DO_FORECAST, DO_POINTS, sign_extra_do, "DO", empty_do,
                                requested_blockout_do)
            flash("Forecast have been generated, you may download it in the page", category='success')
            return redirect(url_for('views.duty_home'))
        elif choosing_do_doo == 'download':
            return redirect(url_for('views.download_file_duty'))
        elif choosing_do_doo == 'amendment_forecast':
            return redirect(url_for('views.duty_plan_do_forecast'))
        elif choosing_do_doo == 'remove':
            return redirect(url_for('views.duty_remove'))
        elif choosing_do_doo == 'amend':
            return redirect(url_for('views.duty_amend'))
        elif choosing_do_doo == 'add':
            return redirect(url_for('views.duty_add'))
    return render_template("duty_main.html", user=current_user)


@views.route('/duty_planner/do/forecast', methods=["GET", "POST"])
def duty_plan_do_forecast():
    dictionary = dict()
    names_in_database = []
    excel_to_dictionary(DO_FORECAST, dictionary)
    generate_names_list(DO_db, names_in_database)
    label = 'Duty Orderly Clerk'
    if request.method == 'POST':
        activity = str(request.form['activity'])
        if activity == 'activate':
            activate_date = str(request.form['activate_first_day'])
            activated_name = str(request.form['activate_first_name' + str(activate_date[12:])])
            standby_activate(str(activate_date[12:]), activated_name, DO_db, DO_FORECAST)
            flash("Standby Activated", category='success')
            return redirect(url_for('views.duty_plan_do_forecast'))
        elif activity == 'swap':
            first_day = str(request.form['first_day'])
            first_name = str(request.form['first_name' + str(first_day[3:])])
            second_day = str(request.form['second_day'])
            second_name = str(request.form['second_name' + str(second_day[10:])])
            if str(first_day[3:]) == str(second_day[10:]):
                flash("Both days cannot be the same", category='error')
            elif int(first_day[3:]) > int(second_day[10:]):
                flash("Please input the earlier date first", category='error')
            else:
                swap_duty(str(first_day[3:]), first_name, str(second_day[10:]), second_name, DO_db, DO_FORECAST)
                flash("Swap Successful", category='success')
                return redirect(url_for('views.duty_plan_do_forecast'))
        elif activity == 'change':
            change_day = str(request.form['change_first_day'])
            current_name = str(request.form['change_first_name' + str(change_day[10:])])
            change_name = str(request.form['change_name'])
            if current_name == change_name:
                flash("Both names are the same", category='error')
            else:
                exchange_personnel(str(change_day[10:]), current_name, change_name, DO_db, DO_FORECAST)
                flash("Personnel Changed", category='success')
                return redirect(url_for('views.duty_plan_do_forecast'))
        elif activity == 'change_standby':
            change_standby_day = str(request.form['change_standby_first_day'])
            current_standby_name = str(request.form['change_standby_first_name' + str(change_standby_day[18:])])
            change_standby_name = str(request.form['change_standby_name'])
            if current_standby_name == change_standby_name:
                flash("Both names are the same", category='error')
            else:
                exchange_personnel_standby(str(change_standby_day[18:]), current_standby_name, change_standby_name,
                                           DO_db, DO_FORECAST)
                flash("Personnel Changed", category='success')
                return redirect(url_for('views.duty_plan_do_forecast'))
    return render_template("duty_amend_current_list.html", user=current_user, dictionary=dictionary, names_in_database=names_in_database, label=label)


@views.route('/duty_blockout_do', methods=["GET", "POST"])
def duty_blockout_do():
    dictionary = requested_blockout_do
    label = 'Duty Orderly Clerk'
    accepted_blockout_display = dict()
    generate_blockout_display(DO_db, accepted_blockout_display)
    if request.method == 'POST':
        for name, reasons in dictionary.copy().items():
            try:
                accept_reject = str(request.form[str(name).upper()])
            except KeyError:
                continue
            if accept_reject == 'Accept':
                accepted_blockout(name, dictionary, DO_db)
                dictionary.pop(name)
            elif accept_reject == 'Reject':
                dictionary.pop(name)
        flash("Acceptance / Rejection have been processed", category='success')
        return redirect(url_for('views.duty_home'))
    return render_template("duty_blockout.html", user=current_user, dictionary=dictionary, len=len, label=label, accepted_blockout_display=accepted_blockout_display)


@views.route('/duty_remove', methods=["GET", "POST"])
def duty_remove():
    name_list_do = []
    generate_names_list(DO_db, name_list_do)
    if request.method == 'POST':
        delete_name_do = str(request.form['delete_name_do']).upper()
        if delete_name_do == 'Choose your option':
            flash("Please select from the options provided.", category='error')
        else:
            duty_delete_name(delete_name_do, DO_db)
            flash("Personnel has been removed from the database.", category='success')
            return redirect(url_for('views.duty_remove'))
    return render_template("duty_remove.html", user=current_user, name_list_do=name_list_do)


@views.route('/duty_amend', methods=["GET", "POST"])
def duty_amend():
    name_list_do = []
    generate_names_list(DO_db, name_list_do)
    if request.method == 'POST':
        rank = str(request.form['rank']).upper()
        name = str(request.form['name']).upper()
        branch = str(request.form['branch']).upper()
        if rank + ' ' + name in name_list_do:
            flash("Personnel is already inside the database.", category='error')
        elif rank == 'Choose your option' or branch == 'Choose your option':
            flash("Please select from the options provided.", category='error')
        else:
            amend_name_do = str(request.form['amend_name_do']).upper()
            duty_amend_name_depot(rank, amend_name_do, name, branch, DO_db)
            flash("Personnel details have been amended.", category='success')
            return redirect(url_for('views.duty_amend'))
    return render_template("duty_amend.html", user=current_user, name_list_do=name_list_do, ranking=ranking, branches_string=branches_string,
                           dropdown_branch=dropdown_branch)


@views.route('/duty_add', methods=["GET", "POST"])
def duty_add():
    name_list_do = []
    generate_names_list(DO_db, name_list_do)
    if request.method == 'POST':
        rank = str(request.form['rank_duty']).upper()
        name = str(request.form['name_duty']).upper()
        name2 = str(request.form['name2_duty']).upper()
        branch = str(request.form['branch']).upper()
        excuse = str(request.form['excuse']).upper()
        if name != name2:
            flash("Please ensure that the name and the confirmation name are the same.", category='error')
        elif rank + ' ' + name in name_list_do:
            flash("Personnel is already inside the database.", category='error')
        elif rank == 'Choose your option' or branch == 'Choose your option' or excuse == 'Choose your option':
            flash("Please select from the options provided.", category='error')
        else:
            duty_insert(rank+' '+name, 1, 0, 0, 0, excuse, branch, DO_db)
            flash("Personnel has been added into the database.", category='success')
    return render_template("duty_add.html", user=current_user, ranking=ranking,  branches_string=branches_string,
                           dropdown_branch=dropdown_branch)


@views.route('/download/duty', methods=["GET", "POST"])
def download_file_duty():
    p = "Duty Roster.xlsx"
    return send_file(p, as_attachment=True)


@views.route('/portfolio', methods=["GET", "POST"])
def portfolio():
    if request.method == 'POST':
        procedure = str(request.form['portfolio_button'])
        if procedure == 'attendance':
            return redirect(url_for('views.index'))
        elif procedure == 'roster':
            return redirect(url_for('views.duty_home'))
        elif procedure == 'resume':
            return redirect(url_for('views.download_file_resume'))
    return render_template("portfolio.html", user=current_user)


@views.route('/download/resume', methods=["GET", "POST"])
def download_file_resume():
    p = "Keagan's Resume.pdf"
    return send_file(p, as_attachment=True)
