import streamlit as st
import streamlit_authenticator as stauth
from datetime import date, timedelta, datetime
import sqlite3
import pandas as pd

# shift setup
shifts = ["Off", "Day Shift", "Night Shift"]
schedules = [shift for shift in shifts for _ in range(2)]
db_file = "users.db"


def show_schedule(dt):
    base_date = date(2023, 7, 17) # date when last off
    start = dt - timedelta(days=2)
    output = "| Date | Day | Schedule |\n| ------ | ------ | -------- |\n"

    for i in range(5):
        thisday = start + timedelta(days=i)
        cycle = thisday - base_date
        if thisday == dt:
            output += f"| **{thisday.strftime('%A')}** | **{thisday}** | **{schedules[cycle.days % 6]}** |\n"
        else:
            output += f"| {thisday.strftime('%A')} | {thisday} | {schedules[cycle.days % 6]} |\n"

    return  output


def get_current_user(email):
    qry = f"SELECT * FROM users WHERE email = '{email}'"
    db = sqlite3.connect(db_file)
    result = pd.read_sql_query(qry, db).to_dict("records")[0]
    return result


def update_date(email, dt):
    qry = f"UPDATE users SET last_off_day = '{dt}' WHERE email = '{email}'"
    db = sqlite3.connect(db_file)
    cur = db.cursor()
    with db:
        cur.execute(qry)
    return cur.rowcount
    

def main_app(email):
    # sidebar settings
    c_user = get_current_user(email)
    try:
        dt = datetime.strptime(c_user["last_off_day"], "%Y-%m-%d")
    except:
        dt = None

    with st.sidebar.expander("Settings"):
        base_date = st.date_input("Your last off day", max_value=date.today(), value=dt)
        update = st.button("Update")
        if update:
            res = update_date(email, base_date)
            if res == 1:
                st.success("Your last off day was set")
            else:
                st.warning("Something went wrong setting your last off day. Please try again.")

    col1, col2 = st.columns([3, 1])
    dt = col1.date_input("Choose a date: ", value=date.today(), min_value=date.today())
    col2.header(" ")
    show = col2.button("Get schedule")
    if show:
        st.write(show_schedule(dt))


def create_credentials():
    # user authetication
    db = sqlite3.connect(db_file)
    qry = "SELECT rowid, * FROM users"
    result = pd.read_sql_query(qry, db)

    u = {}
    for i in range(len(result)):
        u[result.loc[i]["email"]] = {
            "name": result.loc[i]["name"],
            "password": result.loc[i]["hashedpwd"],
        }

    return {"usernames": u}


authenticator = stauth.Authenticate(create_credentials(),
    cookie_name='current_user', key='some_signature_key')

name, authentication_status, email = authenticator.login('Login', 'sidebar')

if authentication_status:
    authenticator.logout('Logout', 'main')
    st.header(f"{name}'s Shedule Check")
    main_app(email)
elif authentication_status == False:
    st.error('Username/password is incorrect')
elif authentication_status == None:
    st.warning('Please enter your username and password')

