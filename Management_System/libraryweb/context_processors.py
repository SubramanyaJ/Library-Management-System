def session_lib_num(request):
    """
    Context processor to provide the logged-in user's `lib_num` if available.
    """
    if request.user.is_authenticated:
        # Fetch `lib_num` from the authenticated user
        return {'lib_num': getattr(request.user, 'lib_num', None)}
    else:
        # Fallback to session storage if needed (optional, if you rely on session)
        return {'lib_num': request.session.get('lib_num', None)}