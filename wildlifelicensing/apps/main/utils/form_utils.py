from django.template import loader, Context
from django.core.context_processors import media as media_processor


class FieldItem(object):
    """ 
    An item inside a ``FieldGroup``
    """
    def __init__(self, form, fielditem):
        self.form = form
        self.fielditem = fielditem

    def __unicode__(self):
        tpl = self.form.get_field_template()
        context_dict = dict(
            form=self.form,
            field=self.form[self.fielditem],
        )
        context_dict.update(media_processor(None))
        return tpl.render(
            Context(
                context_dict
            )
        )


class FieldGroup(object):
    """
    A group of fields yielded by ``StackedForm``
    """
    def __init__(self, form, label, group):
        self.form = form
        self.label = label
        self.group = group

    def __iter__(self):
        for fielditem in self.group.get('fields', ()):
            yield FieldItem(self.form, fielditem)

    def __len__(self):
        # ... or the for templatetag throws an error
        return len(self.group.get('fields', ()))

    def __getattr__(self, name):
        return self.group.get(name, None)

    def __unicode__(self):
        tpl = self.form.get_field_group_template()
        context_dict = dict(
            form=self.form,
            label=self.label,
            fields=[self.form[fielditem] for fielditem in self.group],
        )
        context_dict.update(media_processor(None))
        return tpl.render(
            Context(
                context_dict
            )
        )


class FieldConditionalGroup(object):
    """
    A group of fields yielded by ``StackedForm`` that are shown if a condition is met
    """
    def __init__(self, form, label, group):
        self.form = form
        self.label = label
        self.group = group

    def __iter__(self):
        for fielditem in self.group.get('fields', ()):
            yield FieldItem(self.form, fielditem)

    def __len__(self):
        # ... or the for templatetag throws an error
        return len(self.group.get('fields', ()))

    def __getattr__(self, name):
        return self.group.get(name, None)

    def __unicode__(self):
        tpl = self.form.get_conditional_field_group_template()
        context_dict = dict(
            form=self.form,
            label=self.label,
            fields=[self.form[fielditem] for fielditem in self.group],
        )
        context_dict.update(media_processor(None))
        return tpl.render(
            Context(
                context_dict
            )
        )

class StackedForm(object):
    """
    Mixin to provide support for stacked forms with or without grouped fields.
    One particular example of such a form (without groups though) is the Basecamp
    signup page https://signup.37signals.com/basecamp/Plus/signup/new 
        
    Example:
    
        # ---------------------------------------------------------- Django form
    
        from django import forms
        from toolbox.forms import StackedForm
        
        class MyForm(forms.Form, StackedForm):
            username = forms.CharField()
            pw1 = forms.CharField()
            pw2 = forms.CharField()
            email1 = forms.CharField()
            email2 = forms.CharField()
            first_name = forms.CharField()
            last_name = forms.CharField()
            website = forms.CharField()
            twitter = forms.CharField()
            facebook = forms.CharField()
            
            class Stack:
                stack = (
                    dict(
                        label = 'User Information',
                        fields = ('username',('first_name','last_name'))
                    ),
                    dict(
                        label = 'Security Information',
                        css_class = 'smaller-h1',
                        fields = (('email1','email2'),('pw1','pw2'))
                    ),
                    dict(
                        label = 'Elsewhere',
                        fields = ('website','twitter','facebook')
                    )
                )
        
        # ------------------------------------------------------------- Template
        
        <form action="." method="POST">
            {{ form.as_stack }}
            <input type="submit" value="Submit" />
        </form>
        
        # ---------------------------------------------------- stacked_form.html
        
        <ul>
        {% for stack in form.get_stacks %}
            {% if stack.label %}
                <li>
                    <h1{% if stack.css_class %} class="{{ stack.css_class }}"{% endif %}>{{ stack.label }}</h1>
                </li>
            {% endif %}
            <li>
                <ul>
                    {% for field in stack %}
                        <li>
                            {% if field.is_group %}
                                <ul>
                                    {% for f in field %}
                                        <li>{{ f }}</li>
                                    {% endfor %}
                                </ul>
                            {% else %}
                                {{ field }}
                            {% endif %}
                        </li>
                    {% endfor %}
                </ul>
            </li>
        {% endfor %}
        </ul>
        
        # ----------------------------------------------------- stack_field.html
        
        <p{% if field.errors %} class="error"{% endif %}>
            <label for="{{ field.auto_id }}">{{ field.label.title }}</label>
            {{ field }}
            <span class="tooltip-help">{{ field.help_text }}</span>
        </p>
        
        # --------------------------------------------------------------- Output
        <ul>
            <li>
                <h1>User Information</h1>
            </li>
            <li>
                <ul>
                    <li>
                        <p>
                            <label for="id_username">Username</label>
                            <input type="text" name="username" id="id_username" />
                            <span class="tooltip-help"></span>
                        </p>
                    </li>
                    <li>
                        <ul>
                            <li>
                                <p>
                                    <label for="id_first_name">First Name</label>
                                    <input type="text" name="first_name" id="id_first_name" />
                                    <span class="tooltip-help"></span>
                                </p>
                            </li>                                                    
                            <li>
                                <p>
                                    <label for="id_last_name">Last Name</label>
                                    <input type="text" name="last_name" id="id_last_name" />
                                    <span class="tooltip-help"></span>
                                </p>
                            </li>
                        </ul>
                    </li>
                </ul>
            </li>
            <li>
                <h1 class="smaller-h1">Security Information</h1>
            </li>
            <li>
                <ul>
                    <li>
                        <ul>
                            <li>
                                <p>
                                    <label for="id_email1">Email1</label>
                                    <input type="text" name="email1" id="id_email1" />
                                    <span class="tooltip-help"></span>
                                </p>
                            </li>
                            <li>
                                <p>
                                    <label for="id_email2">Email2</label>
                                    <input type="text" name="email2" id="id_email2" />
                                    <span class="tooltip-help"></span>
                                </p>
                            </li>                            
                        </ul>
                    </li>
                    <li>
                        <ul>
                            <li>
                                <p>
                                    <label for="id_pw1">Pw1</label>
                                    <input type="text" name="pw1" id="id_pw1" />
                                    <span class="tooltip-help"></span>
                                </p>
                            </li>
                            <li>
                                <p>
                                    <label for="id_pw2">Pw2</label>
                                    <input type="text" name="pw2" id="id_pw2" />
                                    <span class="tooltip-help"></span>
                                </p>    
                            </li>
                        </ul>
                    </li>            
                </ul>
            </li>
            <li>
                <h1>Elsewhere</h1>
            </li>
            <li>
                <ul>
                    <li>
                        <p>
                            <label for="id_website">Website</label>
                            <input type="text" name="website" id="id_website" />
                            <span class="tooltip-help"></span>
                        </p>
                    </li>
                    <li>                                            
                        <p>
                            <label for="id_twitter">Twitter</label>
                            <input type="text" name="twitter" id="id_twitter" />
                            <span class="tooltip-help"></span>
                        </p>                    
                    </li>            
                    <li>                    
                        <p>
                            <label for="id_facebook">Facebook</label>
                            <input type="text" name="facebook" id="id_facebook" />
                            <span class="tooltip-help"></span>
                        </p>            
                    </li>            
                </ul>
            </li>
        </ul>        
    """

    field_item_template = 'stackedform/field.html'
    field_group_template = 'stackedform/field_group.html'
    conditional_field_group_template = 'stackedform/conditional_field_group.html'

    def get_field_template(self):
        if getattr(self, '_field_tpl', None) is None:
            self._field_tpl = loader.get_template(self.field_item_template)
        return self._field_tpl

    def get_field_group_template(self):
        if getattr(self, '_field_group_tpl', None) is None:
            self._field_group_tpl = loader.get_template(self.field_group_template)
        return self._field_group_tpl

    def get_conditional_field_group_template(self):
        if getattr(self, '_conditional_field_group_template', None) is None:
            self._conditional_field_group_template = loader.get_template(self.conditional_field_group_template)
        return self._conditional_field_group_template

    def get_items(self):
        for item in self.Stack.stack:
            if item.get('type') == 'field':
                yield FieldItem(self, item.get('field'))
            elif item.get('type') == 'group':
                yield FieldGroup(self, item.get('label'), item.get('fields'))
            elif item.get('type') == 'conditional_group':
                yield FieldConditionalGroup(self, item.get('label'), item.get('fields'))

    def __iter__(self):
        """ If this is the first inherit we can loop directly, else we'd have
        to use ``get_stacks`` """
        return self.get_stacks()
