from website import create_app
import atexit
from apscheduler.schedulers.background import BackgroundScheduler
from parade_state_function import attendance_records, recorded_absences, period_submission_generator, branches_string
from excel_formating import excel_monthly_reset, type_xl_ps, save_file, tracking_delete, block_weekend_excel
import datetime


#  hold functions that run daily, at 1500 hours
def automated():
    time_now = datetime.datetime.now()
    hour_now = time_now.strftime("%H")
    # server and Singapore time is different by 8 hours
    difference_SG_UTC = 8
    if str(int(hour_now)+difference_SG_UTC) == "15":
        print('Refreshed')
        # clear the dictionaries daily
        attendance_records.clear()
        recorded_absences.clear()
        period_submission_generator()
        tracking_delete()
        # function in Excel that runs daily
        for worksheet, branch_string in zip(type_xl_ps, branches_string):
            excel_monthly_reset(worksheet)
            block_weekend_excel(worksheet)
            save_file()
    else:
        print('skipped')


scheduler = BackgroundScheduler()
app = create_app()

if __name__ == '__main__':
    scheduler.add_job(func=automated, trigger="interval", hours=1)
    scheduler.start()
    atexit.register(lambda: scheduler.shutdown())
    app.run(host="0.0.0.0", port=80, debug=True, use_reloader=True)
