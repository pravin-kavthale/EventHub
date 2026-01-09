from  django.contrib.auth import logout
from django.shortcuts import redirect
from django.contrib import messages

#middleware to block users who have been reported more than a threshold
class BlockedUserMiddleware:
    def __init__(self,get_response):
        self.get_response=get_response

    def __call__(self,request):
        profile=getattr(request.user,"profile",None) # if  profile doesnt exists return null

        if (
            profile
            and profile.is_blocked
            and not request.user.is_staff
            and not request.user.is_superuser
        ):

            logout(request)
            messages.error(request,"Your account has been blocked due to multiple reports.")
            return redirect("login")
        return self.get_response(request)
    