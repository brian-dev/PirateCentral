from flask_wtf import FlaskForm
from wtforms.fields.choices import SelectMultipleField
from wtforms.fields.simple import StringField, SubmitField
from wtforms.validators import DataRequired, Length

class AddPlayerForm(FlaskForm):
    first_name = StringField(
        'First Name',
        validators=[DataRequired(), Length(min=2, max=80)],
        render_kw={"placeholder": "Enter first name"}
    )
    last_name = StringField(
        'Last Name',
        validators=[DataRequired(), Length(min=2, max=80)],
        render_kw={"placeholder": "Enter last name"}
    )
    position = StringField(
        'Position',
        validators=[DataRequired(), Length(min=2, max=80)],
        render_kw={"placeholder": "Enter position"}
    )
    team_ids = SelectMultipleField(
        'Teams',
        choices=[],  # Will be populated in the route
        coerce=int,
        validators=[DataRequired(message="Select at least one team")]
    )
    submit = SubmitField('Add Player')


class EditPlayerForm(AddPlayerForm):
    submit = SubmitField('Save Changes')
