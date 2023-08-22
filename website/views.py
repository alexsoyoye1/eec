from flask import Blueprint, flash, render_template, request, flash, redirect, url_for, make_response
from flask_login import login_required, current_user
from website.models import ExitEmployees, User, TerminalBenefit
from werkzeug.security import generate_password_hash, check_password_hash

from . import db
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import pdfkit



views = Blueprint('views', __name__)

@views.route('/', methods=['GET', 'POST'])
@login_required
def home():


    return render_template("home.html", user=current_user)

@views.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    if request.method == 'POST':
        if  "form1" in request.form:
            username = request.form.get('username')
            newusername = request.form.get('newusername')
            user = User.query.filter_by(username=current_user.username).first()
            if user:
                if current_user.username == username:
                    user.username=newusername
                    db.session.commit()
                    flash('Username updated successfully!', category='success')
                    
                    return render_template("settings.html", user=current_user)
                else:
                    flash('Incorrect Username', category='error')


        elif "form2" in request.form:
            password = request.form.get('password')
            newpassword = request.form.get('newpassword')

            user = User.query.filter_by(username=current_user.username).first()
            if user:
                if check_password_hash(user.password, password):


                    user.password=generate_password_hash(newpassword,method='sha256')
                    db.session.commit()
                    flash('Password updated successfully!', category='success')
                    
                    return render_template("settings.html", user=current_user)
                else:
                    flash('Incorrect Password', category='error')


    

    return render_template("settings.html", user=current_user)

@views.route('/newexitform', methods=['GET', 'POST'])    
@login_required
def new():
    lm_List =User.query.filter_by(linemanager_status="Yes",head_status = "No")
    x=[]
    for item in lm_List:
        x.append(item.email)
    lm_list=x
    i = 0
    while i < len(lm_list):
        j = i + 1
        while j < len(lm_list):
            if lm_list[i] == lm_list[j]:
                del lm_list[j]
            else:
                j += 1
        i += 1

    if request.method == 'POST':
        employee_id = request.form.get('employee_id')
        staff_name = request.form.get('staff_name')
        location = request.form.get('location')
        department = request.form.get('department')
        confirmed_employee = request.form.get('confirmed_employee')
        employmentdate = request.form.get('employmentdate')
        res_received_date = request.form.get('res_received_date')
        req_notice = request.form.get('req_notice')
        prop_exitdate = request.form.get('prop_exitdate')
        cal_exitdate = request.form.get('cal_exitdate')
        days_inlieu = request.form.get('days_inlieu')
        leave_days = request.form.get('leave_days')
        
        sendto_email = request.form.get('sendto_email')
        

        

        employee = ExitEmployees.query.filter_by(employee_id=employee_id).first()
        if employee:
            flash('Employee exit form already exists', category='error')
        elif len(employee_id) < 3:
            flash('Employee ID must be greater than 3 characters.', category='error')
        elif len(staff_name) < 2:
            flash('First Name must be greater than 1 characters.', category='error')
        
        else:
            new_employee= ExitEmployees(employee_id=employee_id,  staff_name=staff_name, department=department, location=location,
            confirmed_employee=confirmed_employee, employmentdate=employmentdate, res_received_date=res_received_date,
             req_notice=req_notice, sendto="Operations", prop_exitdate=prop_exitdate, cal_exitdate=cal_exitdate, 
             days_inlieu=days_inlieu, leave_days=leave_days,sendto_email=sendto_email, hr_signatory=current_user.staff_name, 
             hr_signatory_email=current_user.email)
            db.session.add(new_employee)
            db.session.commit()
            flash('Form Created!', category='success')
            alert=send_notification(sendto_email,new_employee.hr_signatory )
            flash(alert, category='success')
            
            return redirect(url_for('views.home'))

    return render_template("new.html", user=current_user, lm_list=lm_list)


@views.route('/review', methods=['GET', 'POST'])
@login_required
def review():                                                                                                                                                                                                                                                                                                                                 
   
    exit_employees = ExitEmployees.query.order_by(ExitEmployees.id)
   
    return render_template("review.html", user=current_user, exit_employees=exit_employees)

@views.route('/complete-review', methods=['GET', 'POST'])
@login_required
def c_review():                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                
   
    exit_employees = ExitEmployees.query.filter_by(final_approval_status="Completed")
   
    return render_template("complete_review.html", user=current_user, exit_employees=exit_employees)

@views.route('/terminal-review', methods=['GET', 'POST'])
@login_required
def terminal():
   
    exit_employees = ExitEmployees.query.filter_by(final_approval_status="Approved")
   
    return render_template("terminal_review.html", user=current_user, exit_employees=exit_employees)


@views.route('/calculate/<int:id>', methods=['GET', 'POST'])
@login_required
def calculate(id):
    
    id_to_append = ExitEmployees.query.get_or_404(id)
    if request.method == 'POST':
        id_to_append.final_approval_status="Completed"
        employee_id = id_to_append.employee_id
        staff_name = id_to_append.staff_name
        monthly_netpay = float(request.form.get('monthly_netpay'))
        days_inlieu = int(request.form.get('days_inlieu'))
        payment_inlieu = (monthly_netpay/(365/12))*days_inlieu 
        hold_salary = float(request.form.get('hold_salary'))
        pension_accrued = float(request.form.get('pension_accrued'))
        pension_paid = float(request.form.get('pension_paid'))
        outstanding_pension = pension_accrued - pension_paid
        leave_allowance_accrued = float(request.form.get('leave_allowance_accrued'))
        leave_allowance_paid = float(request.form.get('leave_allowance_paid'))
        leave_allowance = leave_allowance_accrued - leave_allowance_paid
        total_allowance = payment_inlieu + hold_salary + outstanding_pension + leave_allowance
        breakages_damages = float(request.form.get('breakages_damages'))
        days_inlieu_deducted = int(request.form.get('days_inlieu_deducted'))
        salary_inlieu = (monthly_netpay/(365/12))*days_inlieu_deducted
        overpayment = float(request.form.get('overpayment'))
        total_deduction = breakages_damages + salary_inlieu + overpayment
        entitlement = total_allowance - total_deduction
        if (total_allowance-total_deduction)>=outstanding_pension:
            amount_payable = total_allowance - total_deduction
        else:
            amount_payable = outstanding_pension


        pfa = outstanding_pension - overpayment

        if (entitlement-pfa)<=0:
            salary_account = 0
        else:
            salary_account = entitlement-pfa

        benefit = TerminalBenefit.query.filter_by(employee_id=employee_id).first()
        if benefit:
            flash('Employee exit form already exists', category='error')
        
        else:
            newbenefit = TerminalBenefit(employee_id=employee_id,staff_name=staff_name,monthly_netpay=monthly_netpay,
            days_inlieu=days_inlieu,payment_inlieu=payment_inlieu,hold_salary=hold_salary,pension_accrued=pension_accrued,
            pension_paid=pension_paid, outstanding_pension=outstanding_pension,leave_allowance_accrued=leave_allowance_accrued,
            leave_allowance_paid=leave_allowance_paid,leave_allowance=leave_allowance,total_allowance=total_allowance,
            breakages_damages=breakages_damages,days_inlieu_deducted=days_inlieu_deducted,salary_inlieu=salary_inlieu,
            overpayment=overpayment,total_deduction=total_deduction,entitlement=entitlement,amount_payable=amount_payable,
            pfa=pfa,salary_account=salary_account)
            db.session.add(newbenefit)
            db.session.commit()
            flash('Terminal Benefit Calculated!', category='success')
            return redirect(url_for('views.terminal'))
        



    
    return render_template("calculate.html", user=current_user, id_to_append=id_to_append )
 
@views.route('/admin', methods=['GET', 'POST'])
@login_required
def admin():
    if current_user.department=="IT" and current_user.head_status=="Yes":
   
        exit_employees = ExitEmployees.query.order_by(ExitEmployees.id)
        users=User.query.order_by(User.id)
    
        return render_template("admin.html", user=current_user, exit_employees=exit_employees, users=users)
    else:
        flash('You do not have access to this page', category='error')
        return redirect(url_for('views.home'))
    
@views.route('/status', methods=['GET', 'POST'])
@login_required
def status():
   
   
    exit_employees = ExitEmployees.query.order_by(ExitEmployees.id)
    users=User.query.order_by(User.id)
    
    return render_template("status.html", user=current_user, exit_employees=exit_employees, users=users)
 
@views.route('/update_users/<int:id>', methods=['GET', 'POST'])
@login_required
def updateusers(id):

    id_to_update = User.query.get_or_404(id)
    if request.method == 'POST':
        
        

        id_to_update.email = request.form.get('email')
        id_to_update.username = request.form.get('username')
        id_to_update.staff_name = request.form.get('staffName')
        id_to_update.password = generate_password_hash(request.form.get('password1'),method='sha256') 
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      
        id_to_update.location = request.form.get('location')
        id_to_update.department = request.form.get('department')
        id_to_update.linemanager_status=request.form.get('linemanager_status')
        id_to_update.head_status=request.form.get('head_status')

        try:
            db.session.commit()
            flash('Form Updated!', category='success')
            return redirect(url_for('views.admin'))
        except:
            flash('Failed!', category='error')
            return render_template("update_users.html", user=current_user, id_to_update=id_to_update)

    else:
        return render_template("update_users.html", user=current_user, id_to_update=id_to_update)

@views.route('/delete_user/<int:id>', methods=['GET', 'POST'])
@login_required
def delete_user(id):
    user = User.query.filter_by(id=id).first()
    if request.method == 'POST':
        if user:
            db.session.delete(user)
            db.session.commit()
            flash('User Deleted Successfully', category='error')
            return redirect('/admin')
        
    return render_template('delete_user.html', User=user,user=current_user)




@views.route('/update_employees/<int:id>', methods=['GET', 'POST'])
@login_required
def update_employees(id):
    lm_List =User.query.filter_by(linemanager_status="Yes",head_status = "No")
    x=[]
    for item in lm_List:
        x.append(item.email)
    lm_list=x
    i = 0
    while i < len(lm_list):
        j = i + 1
        while j < len(lm_list):
            if lm_list[i] == lm_list[j]:
                del lm_list[j]
            else:
                j += 1
        i += 1

    id_to_update = ExitEmployees.query.get_or_404(id)
    if request.method == 'POST':
        
        

        id_to_update.email = request.form.get('email')
        id_to_update.username = request.form.get('username')
        id_to_update.staff_name = request.form.get('staffName')
        id_to_update.password = generate_password_hash(request.form.get('password1'),method='sha256') 
        
        id_to_update.location = request.form.get('location')
        id_to_update.department = request.form.get('department')
        id_to_update.linemanager_status=request.form.get('linemanager_status')
        id_to_update.head_status=request.form.get('head_status')

        try:
            db.session.commit()
            flash('Form Updated!', category='success')
            return redirect(url_for('views.admin'))
        except:
            flash('Failed!', category='error')
            return render_template("update_employees.html", user=current_user, id_to_update=id_to_update,lm_list=lm_list)

    else:
        return render_template("update_employees.html", user=current_user, id_to_update=id_to_update,lm_list=lm_list)

@views.route('/delete_employee/<int:id>', methods=['GET', 'POST'])
@login_required
def delete_employee(id):
    employee = ExitEmployees.query.filter_by(id=id).first()
    if request.method == 'POST':
        if employee:
            db.session.delete(employee)
            db.session.commit()
            flash('Employee Exit form Deleted Successfully', category='error')
            return redirect('/admin')
        
    return render_template('delete_employee.html', employee=employee,user=current_user)


@views.route('/update/<int:id>', methods=['GET', 'POST'])
@login_required
def update(id):
    exit_employees = ExitEmployees.query.order_by(ExitEmployees.id)
    id_to_update = ExitEmployees.query.get_or_404(id)
    if (request.method == 'POST' and id_to_update.sendto == 'Operations') or (request.method == 'POST' and current_user.linemanager_status == "Yes"
     and current_user.head_status == "Yes" and current_user.department == "HR") or (request.method == 'POST' and current_user.linemanager_status == "Yes"
     and current_user.head_status == "No" and current_user.department != "HR" and (id_to_update.final_approval_status == "Pending" or id_to_update.final_approval_status == "Not Approved")):
        
        id_to_update.bus_damages_recoverable = request.form.get('bus_damages_recoverable')
        id_to_update.bus_cash_recoverable = request.form.get('bus_cash_recoverable')
        id_to_update.id_collected = request.form.get('id_collected')
        id_to_update.uniform_collected = request.form.get('uniform_collected')
        id_to_update.hmo_collected = request.form.get('hmo_collected')

        id_to_update.bus_signatory = current_user.staff_name
        id_to_update.sendto = 'Finance'

        #Add Head of Finance Department
        alert=send_notification("stephen.adisa@pebnic.com", id_to_update.hr_signatory)
        flash(alert, category='success')

        id_to_update.sendto_email = ""

        try:
            db.session.commit()
            flash('Form Updated!', category='success')
            return redirect(url_for('views.home'))
        except:
            flash('Failed!', category='error')
            return render_template("update.html", user=current_user, id_to_update=id_to_update,exit_employees=exit_employees)

    elif request.method == 'POST' and current_user.department == 'Finance':
        
        id_to_update.excess_car_main = request.form.get('excess_car_main')
        id_to_update.fin_damages_recoverable = request.form.get('fin_damages_recoverable')
        id_to_update.fin_cash_recoverable = request.form.get('fin_cash_recoverable')
        id_to_update.other_charges = request.form.get('other_charges')

        id_to_update.fin_signatory = current_user.staff_name

        #Add Head of IT Department
        
        id_to_update.sendto = 'IT'

        alert=send_notification("david.mukoro@pebnic.com", id_to_update.hr_signatory)
        flash(alert, category='success')


        try:
            db.session.commit()
            flash('Form Updated!', category='success')
            return redirect(url_for('views.home'))
        except:
            flash('Failed!', category='error')
            return render_template("update.html", user=current_user, id_to_update=id_to_update,exit_employees=exit_employees)
    
    elif request.method == 'POST' and current_user.department == 'IT':
        id_to_update.laptop_make = request.form.get('laptop_make')
        id_to_update.laptop_sn = request.form.get('laptop_sn')
        id_to_update.phone_make = request.form.get('phone_make')
        id_to_update.phone_sn = request.form.get('phone_sn')
        id_to_update.ipad_make = request.form.get('ipad_make')
        id_to_update.ipad_sn = request.form.get('ipad_sn')
        id_to_update.cug_debt = request.form.get('cug_debt')

        id_to_update.it_signatory = current_user.staff_name

        #Add Head of CS Department
        alert=send_notification("damilola.toriola@pebnic.com", id_to_update.hr_signatory)
        flash(alert, category='success')
        id_to_update.sendto = 'CS'

        try:
            db.session.commit()
            flash('Form Updated!', category='success')
            return redirect(url_for('views.home'))
        except:
            flash('Failed!', category='error')
            return render_template("update.html", user=current_user, id_to_update=id_to_update,exit_employees=exit_employees)
    
    elif request.method == 'POST' and current_user.department == 'CS':
        id_to_update.loan_balance = request.form.get('loan_balance')
        id_to_update.rent_loan = request.form.get('rent_loan')
        id_to_update.car_brand = request.form.get('car_brand')
        id_to_update.car_rn = request.form.get('car_rn')
        id_to_update.car_status = request.form.get('car_status')
        id_to_update.accom_status = request.form.get('accom_status')
        id_to_update.travel_advance = request.form.get('travel_advance')
        id_to_update.pay_employee_notice = request.form.get('pay_employee_notice')
        id_to_update.pay_company_notice = request.form.get('pay_company_notice')

        id_to_update.cs_signatory = current_user.staff_name
        

        # Send Email to HR Signatory
        alert=send_notification(id_to_update.hr_signatory_email,id_to_update.hr_signatory)
        flash(alert, category='success')
        id_to_update.sendto = 'HR'
        

        try:
            db.session.commit()
            flash('Form Updated!', category='success')
            return redirect(url_for('views.home'))
        except:
            flash('Failed!', category='error')
            return render_template("update.html", user=current_user, id_to_update=id_to_update,exit_employees=exit_employees)

    elif request.method == 'POST' and current_user.department == 'HR' :
        id_to_update.hr_id_collected = request.form.get('hr_id_collected')
        id_to_update.hr_uniform_collected = request.form.get('hr_uniform_collected')
        id_to_update.hr_hmo_collected = request.form.get('hr_hmo_collected')
        id_to_update.hr_laptop_collected = request.form.get('hr_laptop_collected')
        id_to_update.hr_phone_collected = request.form.get('hr_phone_collected')
        id_to_update.hr_ipad_collected = request.form.get('hr_ipad_collected')
        id_to_update.hr_car_collected = request.form.get('hr_car_collected')
        id_to_update.hr_remarks = request.form.get('hr_remarks')
        id_to_update.final_approval_status = request.form.get('final_approval_status')
       

        
        
        

        try:
            db.session.commit()
            flash('Form Updated!', category='success')
            return redirect(url_for('views.home'))
        except:
            flash('Failed!', category='error')
            return render_template("update.html", user=current_user, id_to_update=id_to_update,exit_employees=exit_employees)

    

    else:
        return render_template("update.html", user=current_user, id_to_update=id_to_update,exit_employees=exit_employees)
        

@views.route('/approved', methods=['GET', 'POST'])
@login_required
def approved():
   
    exit_employees = ExitEmployees.query.order_by(ExitEmployees.id)
   
    return render_template("approved.html", user=current_user, exit_employees=exit_employees)
        


@views.route('/report/<int:id>', methods=['GET', 'POST'])
def report(id):
    exit_employees = ExitEmployees.query.order_by(ExitEmployees.id)
    id_to_update = ExitEmployees.query.get_or_404(id)
    
    
    return render_template("report.html", user=current_user, id_to_update=id_to_update,exit_employees=exit_employees)

@views.route('/statement/<id>', methods=['GET', 'POST'])
def statement(id):
    
    id_to_view = TerminalBenefit.query.filter_by(employee_id=id).first()
    
    return render_template("statement.html", user=current_user, id_to_view=id_to_view)

@views.route('/download/<int:id>')
@login_required
def download(id):
    # PDF options
    
    options = {
        "orientation": "portrait",
        "page-size": "A4",
        "margin-top": "0.5cm",
        "margin-right": "0.1cm",
        "margin-bottom": "0.5cm",
        "margin-left": "0.1cm",
        "encoding": "UTF-8"
    }
    config = pdfkit.configuration(wkhtmltopdf='/usr/bin/wkhtmltopdf')
    
    html = url_for('views.report',_external=True, id=id)
    #
    urllink = str(html)
    
    
    pdf = pdfkit.from_url(urllink, options=options, configuration=config)
    response = make_response(pdf)
    response.headers["Content-Type"] = "application/pdf"
    response.headers["Content-Disposition"] = "inline; filename=Report.pdf"
    
    
    
    
    
    
    # Download the PDF
    return response
        

def send_notification(recipient,initiator):

        user= ExitEmployees.query.filter_by(hr_signatory=initiator).first()

        initiator=initiator
        sender="noreply@pebnic.com"
        recipient=recipient
        password="Officernoreply1"
        message = "This is an email notification, \n You have an EMPLOYEE EXIT CLEARANCE form pending for your review.\n This form was initiated by: "+ initiator
        

        server= smtplib.SMTP("mail.pebnic.com",587)
        server.starttls()
        server.login(sender,password)

        msg = MIMEMultipart()
        msg['From'] = sender
        msg['To'] = recipient
        msg['Cc'] = str(user.hr_signatory_email)
        msg['Subject'] = 'Exit Clearance System Notification' 

        msg.attach(MIMEText(message, 'plain', 'utf-8'))







        server.send_message(msg)
        alert = "Notification sent"

        
        
        
        return alert





