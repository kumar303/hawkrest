def get_auth_header(request):
    return request.META.get('HTTP_AUTHORIZATION', '')


def is_hawk_request(request):
    auth_header = get_auth_header(request)
    return auth_header.startswith('Hawk ')
