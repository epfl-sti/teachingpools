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


def get_user_by_partial_first_name_and_partial_last_name(settings, partial_first_name='', partial_last_name=''):
    print("Searching for '*{}*' '*{}*'".format(partial_first_name, partial_last_name))
    filter='(&(givenName={}*)(sn={}*)(EPFLAccredOrder=1)(!(description=Etudiant)))'.format(partial_first_name, partial_last_name)
    ldap_server = Server(settings.LDAP_SERVER, use_ssl=True, get_info=ALL)
    conn = Connection(ldap_server, auto_bind=True)
    conn.search(settings.LDAP_BASEDN, filter,
                attributes=['uniqueIdentifier', 'uid', 'givenName', 'sn', 'mail'])

    if len(conn.entries) == 0:
        conn.search('c=ch', filter, attributes=['uniqueIdentifier', 'uid', 'givenName', 'sn', 'mail'])
        if len(conn.entries) != 1:
            raise ValueError()
    elif len(conn.entries)!=1:
        raise ValueError()

    entry_to_use = conn.entries[0]
    return_value = dict()
    if entry_to_use['mail']: return_value['mail']=min(entry_to_use['mail'])
    if entry_to_use['uniqueIdentifier']: return_value['sciper']=str(entry_to_use['uniqueIdentifier'])
    if entry_to_use['uid']: return_value['username']=min(entry_to_use['uid'])
    if entry_to_use['sn']: return_value['last_name']=min(entry_to_use['sn'])
    if entry_to_use['givenName']: return_value['first_name']=min(entry_to_use['givenName'])
    return return_value


def is_phd(settings, sciper=''):
    filter = settings.LDAP_PHD_FILTER.format(sciper)
    ldap_server = Server(settings.LDAP_SERVER, use_ssl=True, get_info=ALL)
    conn = Connection(ldap_server, auto_bind=True)
    conn.search(settings.LDAP_PHD_BASEDN, filter, attributes=[])
    return len(conn.entries) > 0
