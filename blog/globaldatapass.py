def get_auth_data(request):
    if 'user' not in request.session:
        return {}
    return {
        'username': request.session['user'].get('username', ''),
        'email': request.session['user'].get('email', ''),
    }

