from django.core.exceptions import ObjectDoesNotExist
from rest_framework.exceptions import ValidationError
from .models import User

class UserService:

    @staticmethod
    def promote_user_to_admin(user_id):
        try:
            user = User.objects.get(id=user_id)
        except ObjectDoesNotExist:
            raise ValidationError("User does not exist")

        if user.is_staff:
            raise ValidationError("User is already an admin")

        user.is_staff = True
        user.is_superuser = True
        user.save()

        return user