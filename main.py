import streamlit as st
import streamlit_authenticator as stauth
from datetime import date, timedelta, datetime
import sqlite3, re
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


def encrypt_password(password):
    return stauth.Hasher([password]).generate()[0]


def create_user(name, email, password):
    qry = f"INSERT INTO users (name, email, hashedpwd) VALUES (:name, :email, :hashedpwd)"
    values = {"name": name, "email": email, "hashedpwd": encrypt_password(password)}
    # execute, commit and close
    db = sqlite3.connect(db_file)
    cur = db.cursor()
    with db:
        cur.execute(qry,values)
    db.close()
    return cur.rowcount


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
    

def main_app(email, name):
    c_user = get_current_user(email)
    try:
        dt = datetime.strptime(c_user["last_off_day"], "%Y-%m-%d")
    except:
        dt = None

    # set last day off
    with st.expander("Set last day off"):
        base_date = st.date_input("Your last off day", max_value=date.today(), value=dt)
        update = st.button("Update")
        if update:
            res = update_date(email, base_date)
            if res == 1:
                st.success("Your last off day was set")
            else:
                st.warning("Something went wrong setting your last off day. Please try again.")


    st.header(f"{name}'s Schedule Check")
    col1, col2 = st.columns([3, 1])
    dt = col1.date_input("Choose a date: ", value=date.today(), min_value=date.today())
    col2.header(" ")
    show = col2.button("Get schedule")
    if show:
        st.write(show_schedule(dt))


def register():
    with st.expander("Don't have an account? Register here"):
        with st.form(key="register", clear_on_submit=False):
            errors = []
            st.subheader(":green[Register]")
            name = st.text_input("Name")
            email = st.text_input("Email")
            pwd1 = st.text_input("Password", type="password")
            pwd2 = st.text_input("Confirm password", type="password")
            signup = st.form_submit_button("Submit")

            if signup:
                if not re.match("^[A-Z][A-Za-z\s'-]{1,30}$", name):
                    errors += ["Your name must only contain letters, spaces, hyphens (-) or apostrophes (')"]
                if not re.match("^[a-z0-9._-]{3,40}@[a-z0-9.-]{3,25}\.[a-z]{2,6}$", email):
                    errors += ["Please input a valid email"]
                if not re.match("^.{8,30}$", pwd1):
                    errors += ["Your password must be at least 8 characters long"]
                if pwd1 != pwd2:
                    errors += ["Your confirmation must be the same as your password"]

                if errors:
                    for error in errors:
                        st.error(f"* {error}")
                else:
                    r = create_user(name, email, pwd1)
                    if r:
                        st.success("You are now registered! Log in with the form above")
                    else:
                        st.error("We're sorry, but something went wrong. Please try again later.")

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

# display header
st.title("Security Shift Scheduler")
# login
authenticator = stauth.Authenticate(create_credentials(),
    cookie_name='current_user', key='some_signature_key')


name, authentication_status, email = authenticator.login('Login', 'main')

if authentication_status:
    authenticator.logout('Logout', 'main')
    main_app(email, name)
elif authentication_status == False:
    st.error('Username/password is incorrect')
    register()
elif authentication_status == None:
    # st.warning('Please enter your username and password')
    register()

with st.expander("What this site is about"):
    st.write("""
            ----
            ## Overview
            For the majority of security personnel, shifts rotate in a steady 6-day cycle:
             * 2 days off
             * 2 day shifts
             * 2 night shifts

            This app calculates your shift for any date in the future.
            
             ## How to use
            1. Register with your name, email address and password. Your email address is your username when logging in.
            2. Once you are registered, log in. You will remain logged in on the site for 30 days unless you log out.
            3. Set your last day off. You only need to do this once and you don't need to change it unless your rotation changes.
            4. Under your name, choose a date in the future that you'd like to see your schedule for. Click "Get schedule" to view how you work that day.
             
            ----
            Thank you for using **Security Shift Scheduler**
            """)
