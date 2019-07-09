import re

from django.core.exceptions import ValidationError


def validate_year_config(value):
    pattern = r'(\d{4})-(\d{4})'
    matchObj = re.match(pattern, value)
    if matchObj:
        year_1 = int(matchObj.group(1))
        year_2 = int(matchObj.group(2))
        if year_2 != (year_1 + 1):
            raise ValidationError('%(value)s is not a valid academic year (both years are not consecutive)',
                                  params={'value': value},)
    else:
        raise ValidationError('%(value)s is not a valid academic year (yyyy-yyyy)',
                              params={'value': value},)
