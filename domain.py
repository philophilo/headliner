import urlparse as urp


# Get sub domain name (name.example.com)
def get_domain_name(url):
    try:
        return urp.urlparse(url).netloc
    except Exception as e:
        return ''
