from flask_wtf import FlaskForm
from wtforms.fields.choices import SelectField
from wtforms.fields.simple import StringField, SubmitField
from wtforms.validators import DataRequired, Length

from app.constants import GRADE_LEVELS


class AddTeamForm(FlaskForm):
    school_id = SelectField('School', choices=[], validators=[DataRequired()])
    grade_level = SelectField('Grade Level', choices=GRADE_LEVELS,
                                   validators=[DataRequired(), Length(max=80)])
    sport = StringField('Sport', validators=[DataRequired(), Length(max=80)])
    submit = SubmitField('Add Team')