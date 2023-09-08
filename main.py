from .models import User, LeaveApplication
from . import db
from flask import Blueprint, render_template, url_for, redirect, request, flash
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash

main = Blueprint('main', __name__)


@main.route('/')
def home():
    if current_user.is_authenticated:
        if current_user.is_admin():
            return redirect(url_for('auth.admin_dashboard'))
        elif current_user.is_employee():
            return redirect(url_for('auth.employee_dashboard'))
    return render_template('home.html')


@main.route('/apply_leave', methods=['GET', 'POST'])
@login_required
def apply_leave():
    if request.method == 'POST':
        date_from = request.form.get('date_from')
        date_to = request.form.get('date_to')
        reason = request.form.get('reason')
        new_leave = LeaveApplication(date_from=date_from, date_to=date_to, reason=reason, user_id=current_user.id)

        db.session.add(new_leave)
        db.session.commit()

        flash('Leave application submitted successfully', 'success')
        return redirect(url_for('main.list_leave'))  # Redirect to the dashboard or another appropriate page after submission

    return render_template('apply_leave.html')  # Display the leave application form

@main.route('/profile')
@login_required  # Use this decorator to ensure the user is logged in
def profile():
    return render_template('profile.html', user=current_user)

@main.route('/applied_leave')
@login_required
def list_leave():
    user_leaves = current_user.leave_applications
    return render_template('applied_leaves.html', leaves=user_leaves)

@main.route('/employee_list', methods=['GET','POST'])
@login_required
def employee_list():
    employees = User.query.filter_by(role='employee').all()
    employees_with_serial_numbers = [(index + 1, employee) for index, employee in enumerate(employees)]
    return render_template('employee_list.html', employees=employees_with_serial_numbers)

@main.route('/add_employee', methods=['GET', 'POST'])
@login_required
def add_employee():
    if request.method == 'POST':
        email = request.form.get('email')
        name = request.form.get('name')
        role = request.form.get('role')
        password = request.form.get('password')
        
        user = User.query.filter_by(email=email).first()
        if user:
            flash("Employee already exists with this email address", 'danger')  # Flash message with danger style
        else:
            new_user = User(email=email, name=name, role=role, password=generate_password_hash(password, method='sha256'))
            db.session.add(new_user)
            db.session.commit()
            flash('Employee Created Successfully', 'success')  # Flash message with success style
            return redirect(url_for('main.employee_list'))

    return render_template('add_employee.html')

@main.route('/employee_leaves')
@login_required
def employee_leaves():
    leaves = LeaveApplication.query.filter_by(status="Pending").all()
    return render_template('employee_leaves.html', leaves=leaves)

@main.route('/update_leave_status/<int:leave_id>/<string:status>')
@login_required
def update_leave_status(leave_id, status):
    # Check if the user is an admin (you can implement your own logic for admin verification)
    if not current_user.is_admin():
        flash('You do not have permission to update leave status.', 'danger')
        return redirect(url_for('main.employee_leaves'))

    # Get the leave application by its ID
    leave = LeaveApplication.query.get_or_404(leave_id)

    # Update the leave status
    leave.status = status
    db.session.commit()

    flash('Leave status updated successfully.', 'success')
    return redirect(url_for('main.employee_leaves'))

@main.route('/update_employee/<int:user_id>', methods=['GET', 'POST'])
@login_required
def update_employee(user_id):
    if not current_user.is_admin():
        flash('You do not have permission to update employees.', 'danger')
        return redirect(url_for('main.employee_list'))

    employee = User.query.get_or_404(user_id)

    if request.method == 'POST':
        employee.name = request.form.get('name')
        employee.email = request.form.get('email')
        db.session.commit()
        flash('Employee information updated successfully.', 'success')
        return redirect(url_for('main.employee_list'))

    return render_template('update_employee.html', employee=employee)

@main.route('/delete_employee/<int:user_id>', methods=['GET', 'POST'])
@login_required
def delete_employee(user_id):
    if not current_user.is_admin():
        flash('You do not have permission to delete employees.', 'danger')
        return redirect(url_for('main.employee_list'))
    if request.method == 'POST':
        employee = User.query.get_or_404(user_id)
        db.session.delete(employee)
        db.session.commit()
        flash('Employee deleted successfully.', 'success')
    return redirect(url_for('main.employee_list'))
