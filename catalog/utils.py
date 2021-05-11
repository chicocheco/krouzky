import unicodedata

from django.utils.text import slugify


def comma_splitter(tag_string):
    return [t.strip().lower() for t in tag_string.split(',') if t.strip()]


def comma_joiner(tags):
    return ', '.join(t.name for t in tags)


def asciify(value):
    return unicodedata.normalize('NFKD', value).encode('ascii', 'ignore').decode('ascii')


def get_slugs(value):
    return [slugify(t.strip()) for t in value.split(',') if t.strip()]
