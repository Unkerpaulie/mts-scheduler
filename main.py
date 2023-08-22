import streamlit as st
import streamlit_authenticator as stauth
from datetime import date, timedelta
import sqlite3
import pandas as pd

shifts = ["Off", "Day Shift", "Night Shift"]
schedules = [shift for shift in shifts for _ in range(2)]

# user authetication


st.header("Siobhan's Shedule Check")

col1, col2 = st.columns([3, 1])

dt = col1.date_input("Choose a date: ", value=date.today(), min_value=date.today())

def show_schedule():
    base_date = date(2023, 7, 17) # date when last off
    start = dt - timedelta(days=2)
    output = "| Date | Day | Schedule |\n| ------ | -------- |\n"

    for i in range(5):
        thisday = start + timedelta(days=i)
        cycle = thisday - base_date
        if thisday == dt:
            output += f"| **{thisday}** | **{schedules[cycle.days % 6]}** |\n"
        else:
            output += f"| {thisday} | {schedules[cycle.days % 6]} |\n"

    return  output

col2.header(" ")
show = col2.button("Get schedule", on_click=show_schedule)

if show:
    st.write(show_schedule())

