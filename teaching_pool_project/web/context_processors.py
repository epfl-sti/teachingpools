from django.conf import settings
from web.helpers import config

def app_base_info(request):
    return {
        'ENVIRONMENT_TYPE': settings.ENVIRONMENT_TYPE,
        'CURRENT_YEAR': config.get_config('current_year'),
        'CURRENT_TERM': config.get_config('current_term'),
        'REQUESTS_FOR_TAS_ARE_OPEN': config.get_config('requests_for_TAs_are_open'),
        'APPLICATIONS_ARE_OPEN': config.get_config('applications_are_open'),
        'PHD_CAN_WITHDRAW_APPLICATION': config.get_config('phds_can_withdraw_applications'),
        'TIME_REPORTING_IS_OPEN': config.get_config('time_reporting_is_open'),
    }
