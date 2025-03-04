from django.contrib.auth.models import BaseUserManager

class UserManager(BaseUserManager):
    def create_user(self, email, first_name, last_name, phone_number, password=None, **extra_fields):
        if email is None:
            raise ValueError("Pole e-mail jest wymagane")
        if first_name is None:
            raise ValueError("Pole imię jest wymagane")
        if last_name is None:
            raise ValueError("Pole nazwisko jest wymagane")
        if phone_number is None:
            raise ValueError("Pole numer telefonu jest wymagane")

        email = self.normalize_email(email)

        user = self.model(
            email=email,
            first_name=first_name,
            last_name=last_name,
            phone_number=phone_number,
            **extra_fields
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, first_name, last_name, phone_number, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        return self.create_user(
            email=email,
            first_name=first_name,
            last_name=last_name,
            phone_number=phone_number,
            password=password,
            **extra_fields
        )