from ldap3 import ALL, Connection, Server


def get_sciper(settings, username):
    ldap_server = Server(settings.LDAP_SERVER, use_ssl=True, get_info=ALL)
    conn = Connection(ldap_server, auto_bind=True)
    conn.search(settings.LDAP_BASEDN, settings.LDAP_FILTER.format(
        username), attributes=['uniqueIdentifier'])

    for entry in conn.entries:
        return str(entry['uniqueIdentifier'])


def get_mail(settings, username):
    ldap_server = Server(settings.LDAP_SERVER, use_ssl=True, get_info=ALL)
    conn = Connection(ldap_server, auto_bind=True)
    conn.search(settings.LDAP_BASEDN, settings.LDAP_FILTER.format(
        username), attributes=['mail'])

    for entry in conn.entries:
        return str(entry['mail'])


def get_usernames(settings, scipers):
    return_value = {}
    filter = "(|"
    for sciper in scipers:
        filter += "(uniqueIdentifier={})".format(sciper)
    filter += ")"
    ldap_server = Server(settings.LDAP_SERVER, use_ssl=True, get_info=ALL)
    conn = Connection(ldap_server, auto_bind=True)
    conn.search(settings.LDAP_BASEDN, filter,
                attributes=['uid', 'uniqueIdentifier'])
    for entry in conn.entries:
        uid = min(entry['uid']).split('@')[0]
        sciper = str(entry['uniqueIdentifier'])
        return_value[sciper] = uid
    return return_value


def get_mails(settings, scipers):
    return_value = {}
    filter = "(|"
    for sciper in scipers:
        filter += "(uniqueIdentifier={})".format(sciper)
    filter += ")"
    ldap_server = Server(settings.LDAP_SERVER, use_ssl=True, get_info=ALL)
    conn = Connection(ldap_server, auto_bind=True)
    conn.search(settings.LDAP_BASEDN, filter,
                attributes=['uniqueIdentifier', 'mail'])
    for entry in conn.entries:
        if entry['mail']:
            mail = min(entry['mail'])
            sciper = str(entry['uniqueIdentifier'])
            return_value[sciper] = mail
    return return_value


def get_users(settings, scipers):
    return_value = list()
    filter = "(&(|"
    for sciper in scipers:
        filter += "(uniqueIdentifier={})".format(sciper)
    filter += ")(EPFLAccredOrder=1))"
    ldap_server = Server(settings.LDAP_SERVER, use_ssl=True, get_info=ALL)
    conn = Connection(ldap_server, auto_bind=True)
    conn.search(settings.LDAP_BASEDN, filter,
                attributes=['uniqueIdentifier', 'mail', 'uid', 'sn', 'givenName'])
    for entry in conn.entries:
        current_result = {}
        current_result['sciper'] = str(entry['uniqueIdentifier'])
        current_result['email'] = min(entry['mail'])
        current_result['username'] = min(entry['uid'])
        current_result['first_name'] = min(entry['givenName'])
        current_result['last_name'] = min(entry['sn'])
        return_value.append(current_result)
    return return_value


def get_user_by_partial_first_name_and_partial_last_name(settings, partial_first_name='', partial_last_name=''):
    print("Searching for '*{}*' '*{}*'".format(partial_first_name, partial_last_name))
    filter = '(&(givenName={}*)(sn={}*)(EPFLAccredOrder=1)(!(description=Etudiant)))'.format(
        partial_first_name, partial_last_name)
    ldap_server = Server(settings.LDAP_SERVER, use_ssl=True, get_info=ALL)
    conn = Connection(ldap_server, auto_bind=True)
    conn.search(settings.LDAP_BASEDN, filter,
                attributes=['uniqueIdentifier', 'uid', 'givenName', 'sn', 'mail'])

    if len(conn.entries) == 0:
        conn.search('c=ch', filter, attributes=[
                    'uniqueIdentifier', 'uid', 'givenName', 'sn', 'mail'])
        if len(conn.entries) != 1:
            raise ValueError()
    elif len(conn.entries) != 1:
        raise ValueError()

    entry_to_use = conn.entries[0]
    return_value = dict()
    if entry_to_use['mail']:
        return_value['mail'] = min(entry_to_use['mail'])
    if entry_to_use['uniqueIdentifier']:
        return_value['sciper'] = str(entry_to_use['uniqueIdentifier'])
    if entry_to_use['uid']:
        return_value['username'] = min(entry_to_use['uid'])
    if entry_to_use['sn']:
        return_value['last_name'] = min(entry_to_use['sn'])
    if entry_to_use['givenName']:
        return_value['first_name'] = min(entry_to_use['givenName'])
    return return_value


def is_phd(settings, sciper=''):
    filter = settings.LDAP_PHD_FILTER.format(sciper)
    ldap_server = Server(settings.LDAP_SERVER, use_ssl=True, get_info=ALL)
    conn = Connection(ldap_server, auto_bind=True)
    conn.search(settings.LDAP_PHD_BASEDN, filter, attributes=[])
    return len(conn.entries) > 0


def get_user_by_username_or_sciper(settings, input):
    filter = "(|"
    filter += "(uniqueIdentifier={})".format(input)
    filter += "(uid={})".format(input)
    filter += ")"
    ldap_server = Server(settings.LDAP_SERVER, use_ssl=True, get_info=ALL)
    conn = Connection(ldap_server, auto_bind=True)
    conn.search(settings.LDAP_BASEDN, filter, size_limit=1, attributes=[
                'sn', 'givenName', 'uid', 'uniqueIdentifier', 'mail'])
    if len(conn.entries) == 0:
        return "No entry found"
    elif len(conn.entries) == 1:
        entry = conn.entries[0]
        return_value = dict()
        return_value['sciper'] = str(entry['uniqueIdentifier'])
        return_value['username'] = min(entry['uid'])
        return_value['first_name'] = min(entry['givenName'])
        return_value['last_name'] = min(entry['sn'])
        return_value['mail'] = min(entry['mail'])
        return return_value
    else:
        return "Too many entries returned"


def get_users_by_partial_username_or_partial_sciper(settings, input):
    filter = "(&"
    filter += "(objectClass=EPFLorganizationalPerson)"
    filter += "(|"
    filter += "(uniqueIdentifier={})".format(input)
    filter += "(sn=*{}*)".format(input)
    filter += "(givenName=*{}*)".format(input)
    filter += ")" # of or condition
    filter += ")" # of and condition
    ldap_server = Server(settings.LDAP_SERVER, use_ssl=True, get_info=ALL)
    conn = Connection(ldap_server, auto_bind=True)
    conn.search(settings.LDAP_BASEDN, filter, attributes=[
                'sn', 'givenName', 'uniqueIdentifier'])
    return_value = list()
    for entry in conn.entries:
        if entry['givenName']:
            first_name = min(entry['givenName'])
        else:
            first_name = ''
        last_name = min(entry['sn'])
        sciper = str(entry['uniqueIdentifier'])
        displayed_value = "{}, {} ({})".format(last_name, first_name, sciper)
        return_value.append(displayed_value)

    # deduplicate the entries
    return_value = list(dict.fromkeys(return_value))
    return return_value
