from decimal import Decimal
from flask_wtf import Form
from wtforms import StringField, DecimalField, SelectField, FileField
from wtforms.validators import InputRequired, NumberRange, DataRequired, Optional, \
    ValidationError
from wtforms.widgets import html_params, Select, HTMLString
from .models import Category


# Custom Validator for CategoryForm to create category
def check_duplicate_category(case_sensitive=True):
    def _check_duplicate(form, field):
        if case_sensitive:
            res = Category.query.filter(
                    Category.name.like('%' + field.data + '%')
            ).first()
        else:
            res = Category.query.filter(
                    Category.name.ilike('%' + field.data + '%')
            ).first()
        if res:
            raise ValidationError(
                    'Category named %s already exists' % field.data
            )
    return _check_duplicate


# Widget to create customized label field
class CustomCategoryInput(Select):

    def __call__(self, field, **kwargs):
        kwargs.setdefault('id', field.id)
        html = []
        for val, label, selected in field.iter_choices():
            html.append(
                '<input type="radio" %s> %s' % (
                    html_params(
                        name=field.name, value=val,
                        checked=selected, **kwargs
                    ), label
                )
            )
        return HTMLString(' '.join(html))


# Custom Field for ProductForm to create product
class CategoryField(SelectField):
    widget = CustomCategoryInput()

    def iter_choices(self):
        categories = [(c.id, c.name) for c in
                      Category.query.all()]
        for value, label in categories:
            yield (value, label, self.coerce(value) == self.data)

    def pre_validate(self, form):
        for v, _ in [(c.id, c.name) for c in
                     Category.query.all()]:
            if self.data == v:
                break
        else:
            raise ValueError(self.gettext('Not a valid choice'))


class NameForm(Form):
    name = StringField('Name', validators=[DataRequired()])


class ProductForm(NameForm):
    price = DecimalField('Price', validators=[
        InputRequired(), NumberRange(min=Decimal('0.0'))
    ])
    category = CategoryField(
            'Category', validators=[InputRequired()], coerce=int
    )
    # company = StringField('Company', validators=[Optional])
#     The company field, if you add this field, you must add it to the frontend form, or the
#     validator funciton(form.validate_on_submit() )will raise an error:
#     'TypeError: __init__() takes at most 2 arguments (3 given)'
    image = FileField('Product Image')


class CategoryForm(NameForm):
    name = StringField('Category_name', validators=[
        DataRequired(), check_duplicate_category()])
    pass

