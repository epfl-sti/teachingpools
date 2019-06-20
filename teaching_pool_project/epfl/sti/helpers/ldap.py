from ldap3 import ALL, Connection, Server

def get_sciper(settings, username):
    ldap_server = Server(settings.LDAP_SERVER, use_ssl=True, get_info=ALL)
    conn = Connection(ldap_server, auto_bind=True)
    conn.search(settings.LDAP_BASEDN, settings.LDAP_FILTER.format(username), attributes=['uniqueIdentifier'])

    for entry in conn.entries:
        return str(entry['uniqueIdentifier'])

def get_mail(settings, username):
    ldap_server = Server(settings.LDAP_SERVER, use_ssl=True, get_info=ALL)
    conn = Connection(ldap_server, auto_bind=True)
    conn.search(settings.LDAP_BASEDN, settings.LDAP_FILTER.format(username), attributes=['mail'])

    for entry in conn.entries:
        return str(entry['mail'])
