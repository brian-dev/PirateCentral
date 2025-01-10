from flask import render_template, flash, redirect, url_for, abort
from . import schools_bp


@schools_bp.route('/all_schools')
def all_schools():
    from app.models import School, Team  # Delay import to avoid circular dependencies
    schools = School.query.all()
    teams = Team.query.all()
    return render_template('all_schools.html', teams=teams, schools=schools, enumerate=enumerate)

@schools_bp.route('/schools/<int:school_id>')
def school(school_id):
    from app.models import School
    schools = School.query.order_by(School.id).all()
    current_index = next((i for i, s in enumerate(schools) if s.id == school_id), None)

    if current_index is None:
        abort(404)

    school = schools[current_index]
    previous_school = schools[current_index - 1] if current_index > 0 else None
    next_school = schools[current_index + 1] if current_index < len(schools) - 1 else None

    return render_template(
        'school.html',
        school=school,
        previous_school=previous_school,
        next_school=next_school
    )

@schools_bp.route('/add_school', methods=['GET', 'POST'])
# @role_required("admin")
def add_school():
    from app.models import School  # Delay import to avoid circular dependencies
    from .forms import AddSchoolForm  # Delay import
    from app import db  # Delay import

    form = AddSchoolForm()
    if form.validate_on_submit():
        new_school = School(
            district_name=form.district_name.data,
            school_name=form.school_name.data,
            school_mascot=form.school_mascot.data,
            uil_conference=form.uil_conference.data,
            uil_region=form.uil_region.data,
            uil_district=form.uil_district.data,
        )

        db.session.add(new_school)
        db.session.commit()

        flash(f'School "{new_school.school_name}" added successfully!', 'success')
        return redirect(url_for('schools.add_school'))  # Use blueprint prefix

    return render_template('add_school.html', form=form)

@schools_bp.route('/edit_school/<int:school_id>', methods=['GET', 'POST'])
# @role_required("admin")
def edit_school(school_id):
    from app.models import School
    from app import db
    from .forms import EditSchoolForm
    school = School.query.get_or_404(school_id)
    form = EditSchoolForm(obj=school)

    if form.validate_on_submit():
        school.district_name = form.district_name.data
        school.school_name = form.school_name.data
        school.school_mascot = form.school_mascot.data
        school.uil_conference = form.uil_conference.data
        school.uil_region = form.uil_region.data
        school.uil_district = form.uil_district.data

        db.session.commit()
        flash(f'School "{school.school_name}" updated successfully!', 'success')
        return redirect(url_for('schools.all_schools'))
    return render_template('edit_school.html', form=form, school=school)

