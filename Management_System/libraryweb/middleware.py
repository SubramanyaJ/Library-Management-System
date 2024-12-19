from django.http import HttpResponsePermanentRedirect
from django.urls import resolve
from django.contrib.auth import logout
from django.shortcuts import redirect
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta,datetime
from .models import User
from django.contrib.auth import logout
from django.utils.timezone import now 


import re

class CaseInsensitiveMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Exclude paths starting with '/admin', '/static', '/media',
        # or containing 'LIBNum' (case-insensitive match)
        if not (
            request.path_info.startswith('/admin') or
            request.path_info.startswith('/static') or
            request.path_info.startswith('/media') or
            re.search(r'LIB\d+', request.path_info, re.IGNORECASE)
        ):
            try:
                # Resolve the path to check if it's valid
                resolved_path = resolve(request.path_info)
                if resolved_path:  # If a valid URL match is found
                    # Split the path into segments
                    segments = request.path_info.split('/')

                    # Title-case all segments except those containing LIBNum
                    title_cased_segments = [
                        segment if re.search(r'LIB\d+', segment, re.IGNORECASE) else segment.title()
                        for segment in segments
                    ]

                    # Rejoin the segments into the normalized path
                    normalized_path = '/'.join(title_cased_segments)

                    # Ensure the correct format, and check if any change is needed
                    if request.path_info != normalized_path:
                        # Redirect to the normalized path
                        return HttpResponsePermanentRedirect(normalized_path)
            except Exception:
                pass  # Ignore errors in resolving the path

        # Proceed with the view handling
        response = self.get_response(request)
        return response
    
    
class InactivityLogoutMiddleware:
    """
    Middleware to log out users after a period of inactivity.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated and not request.user.is_superuser:
            last_activity = request.session.get('last_activity')

            if last_activity:
                try:
                    last_activity_time = datetime.fromisoformat(last_activity)
                    inactivity_limit = timedelta(minutes=5)

                    if now() - last_activity_time > inactivity_limit:
                        # Mark the user as inactive if they exceed the inactivity limit
                        if request.user.is_active:
                            request.user.is_active = False
                            request.user.library_profile.is_active = False
                            request.user.save()
                            request.user.library_profile.save()

                        # Logout and clear session (non-flush to preserve data)
                        logout(request)
                        request.session.clear_expired()
                        return redirect('libraryweb:signin')

                except ValueError:
                    # If session data is malformed, reset last_activity
                    request.session['last_activity'] = now().isoformat()

            # Update last activity time
            request.session['last_activity'] = now().isoformat()

        return self.get_response(request)