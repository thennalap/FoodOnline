from django.dispatch import receiver
from django.db.models.signals import post_save
from .models import User,UserProfile


@receiver(post_save,sender=User)
def post_save_create_profile_receiver(sender,instance,created,**kwargs):
    if created:
        print(created,"created value")        
        UserProfile.objects.create(user=instance)
        print("User Profile Created")
    else:
        ## case updated
        print(created,"updated")   
        try:
            profile=UserProfile.objects.get(user=instance)
            profile.save()
            print("user profile updated")
        except:
            print("create userprofile if not exists otherwise gives error")
            UserProfile.objects.create(user=instance)
       