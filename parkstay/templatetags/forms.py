from django import template

register = template.Library()

@register.filter(name='class')
def addClass(value, arg):
    css_classes = value.field.widget.attrs.get('class',None)
    if css_classes:
        css_classes.split(' ')
        if arg not in css_classes:
            css_classes = '%s %s' % (css_classes, arg)
    else:
        css_classes = '%s' % (arg)
    return value.as_widget(attrs={'class': css_classes})
