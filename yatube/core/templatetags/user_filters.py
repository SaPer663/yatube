from django import template

register = template.Library()


@register.filter
def addclass(fiels, css):
    return fiels.as_widget(attrs={'class': css})


@register.filter
def uglify(text):
    result = []
    for i in range(1, len(text) + 1):
        if i % 2 != 0:
            result.append(text[i - 1].lower())
        else:
            result.append(text[i - 1].upper())
    return ''.join(result)
