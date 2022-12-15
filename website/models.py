from email.policy import default

from . import db
from flask_login import UserMixin 
from sqlalchemy.sql import func, text
from datetime import datetime, timedelta


class ExitEmployees(db.Model):
    id = db.Column(db.Integer, primary_key=True) 
    sendto = db.Column(db.String(150))


    #HR Department Fields
    employee_id = db.Column(db.String(150), unique=True)
    staff_name = db.Column(db.String(150))
    department = db.Column(db.String(150))
    location = db.Column(db.String(150))
    confirmed_employee=db.Column(db.String(20))
    employmentdate = db.Column(db.String(150))
    res_received_date = db.Column(db.String(150)) 
    req_notice = db.Column(db.Integer)  
    prop_exitdate = db.Column(db.String(150))
    cal_exitdate = db.Column(db.String(150))
    days_inlieu =db.Column(db.Integer) 
    leave_days = db.Column(db.Integer) 
    sendto_name = db.Column(db.String(150))
    sendto_email = db.Column(db.String(150))
    hr_signatory = db.Column(db.String(150))
    hr_signatory_email = db.Column(db.String(150))

    #Business Department Fields
    bus_damages_recoverable = db.Column(db.Integer)
    bus_cash_recoverable = db.Column(db.Integer)
    id_collected = db.Column(db.String(20))
    uniform_collected = db.Column(db.String(20))
    hmo_collected = db.Column(db.String(20))
    bus_signatory = db.Column(db.String(150))

    #Finance Department Fields
    
    excess_car_main = db.Column(db.Integer)
    fin_damages_recoverable = db.Column(db.Integer)
    fin_cash_recoverable = db.Column(db.Integer)
    other_charges = db.Column(db.Integer)
    fin_signatory = db.Column(db.String(150))
    
    #IT Department Fields
    laptop_make = db.Column(db.String(150))
    laptop_sn = db.Column(db.String(150))
    phone_make = db.Column(db.String(150))
    phone_sn = db.Column(db.String(150))
    ipad_make = db.Column(db.String(150))
    ipad_sn = db.Column(db.String(150))
    cug_debt = db.Column(db.Integer)
    it_signatory = db.Column(db.String(150))

    #CS Department Fields
    loan_balance = db.Column(db.Integer)
    rent_loan = db.Column(db.Integer)
    car_brand = db.Column(db.String(150))
    car_rn = db.Column(db.String(150))
    car_status = db.Column(db.String(150))
    accom_status = db.Column(db.String(150))
    travel_advance = db.Column(db.String(150))
    pay_employee_notice = db.Column(db.Integer)
    pay_company_notice = db.Column(db.Integer)
    cs_signatory = db.Column(db.String(150))

    #HR FINAL REVIEW Department Fields
    hr_id_collected = db.Column(db.String(20))
    hr_uniform_collected = db.Column(db.String(20))
    hr_hmo_collected = db.Column(db.String(20))
    hr_laptop_collected = db.Column(db.String(20))
    hr_phone_collected = db.Column(db.String(20))
    hr_ipad_collected = db.Column(db.String(20))
    hr_car_collected = db.Column(db.String(20))
    hr_remarks = db.Column(db.String(10000))
    final_approval_status = db.Column(db.String(50))










class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150))
    username = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    staff_name = db.Column(db.String(150))
    department = db.Column(db.String(150))
    location = db.Column(db.String(150))
    linemanager_status = db.Column(db.String(150))
    head_status = db.Column(db.String(150))
    
