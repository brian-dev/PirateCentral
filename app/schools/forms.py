from flask_wtf import FlaskForm
from wtforms.fields.choices import SelectField
from wtforms.fields.simple import StringField, SubmitField
from wtforms.validators import DataRequired, Length

from app.constants import UIL_CONFERENCES, UIL_REGIONS, UIL_DISTRICTS


class AddSchoolForm(FlaskForm):
    district_name = StringField('District Name', validators=[DataRequired(), Length(max=80)],
                                render_kw={"placeholder": "Example ISD"})
    school_name = StringField('School Name', validators=[DataRequired(), Length(max=80)],
                              render_kw={"placeholder": "Example High School"})
    school_mascot = StringField('School Mascot', validators=[DataRequired(), Length(max=80)],
                                render_kw={"placeholder": "Bobcats"})
    uil_conference = SelectField('UIL Conference', choices=UIL_CONFERENCES,
                                 validators=[DataRequired(message='UIL Conference is required')])
    uil_region = SelectField('UIL Region', choices=UIL_REGIONS,
                             validators=[DataRequired(message='Please select a region')])
    uil_district = SelectField('UIL District', choices=UIL_DISTRICTS,
                               validators=[DataRequired(message='Please select a district')])
    submit = SubmitField('Add School')

class EditSchoolForm(AddSchoolForm):
    submit = SubmitField('Save Changes')