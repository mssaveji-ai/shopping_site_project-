def get_ip(request):
    X_FORWARDED_FOR = request.META.get('HTTP_X_FORWARDED_FOR')
    if X_FORWARDED_FOR:
        ip = X_FORWARDED_FOR.split(',')[0].strip()
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip