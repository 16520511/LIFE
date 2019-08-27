from django.db import models
from django.contrib.auth.models import (
    BaseUserManager, AbstractBaseUser
)
import uuid


class MyUserManager(BaseUserManager):
    def create_user(self, email, date_of_birth, first_name, last_name, gender, password=None):
        """
        Creates and saves a User with the given email, date of
        birth and password.
        """
        if not email:
            raise ValueError('Users must have an email address')

        user = self.model(
            email=self.normalize_email(email),
            date_of_birth=date_of_birth,
            first_name = first_name,
            last_name = last_name,
            gender = gender,
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, date_of_birth, first_name, last_name, gender, password):
        """
        Creates and saves a superuser with the given email, date of
        birth and password.
        """
        user = self.create_user(
            email,
            password=password,
            date_of_birth=date_of_birth,
            first_name = first_name,
            last_name = last_name,
            gender = gender,
        )
        user.is_admin = True
        user.save(using=self._db)
        return user


class MyUser(AbstractBaseUser):
    GENDER_CHOICES = (
        ('Male', 'Male'),
        ('Female', 'Female'),
    )
    email = models.EmailField(
        verbose_name='email address',
        max_length=255,
        unique=True,
    )
    date_of_birth = models.DateField()
    first_name = models.CharField(max_length = 25)
    last_name = models.CharField(max_length = 25)
    gender = models.CharField(max_length = 25, choices = GENDER_CHOICES, default = 'Male')
    profile_name = models.SlugField(unique = True)

    followings = models.ManyToManyField("self", symmetrical = False, related_name='followers')

    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)

    objects = MyUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['date_of_birth', 'last_name', 'first_name', 'gender']

    def user_directory_path(instance, filename):
        # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
        return 'user_{0}/{1}'.format(instance.profile_name, filename)

    # avatar = models.ImageField(upload_to=user_directory_path, max_length=100, blank=True, default='default/default-avatar.png')
    avatar = models.URLField(default='https://i.ibb.co/vxKKNwk/tt-avatar-small.jpg')
    def __str__(self):
        return self.profile_name

    def has_perm(self, perm, obj=None):
        # "Does the user have a specific permission?"
        # Simplest possible answer: Yes, always
        return True

    def has_module_perms(self, app_label):
        # "Does the user have permissions to view the app `app_label`?"
        # Simplest possible answer: Yes, always
        return True

    @property
    def is_staff(self):
        # "Is the user a member of staff?"
        # Simplest possible answer: All admins are staff
        return self.is_admin

    def get_followings(self):
        return ",".join([str(p) for p in self.followings.all()])

    def __unicode__(self):
        return "{0}".format(self.title)

class Post(models.Model):
    id = models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, verbose_name='UUID')
    user = models.ForeignKey(MyUser, on_delete = models.CASCADE)
    text_content = models.TextField()
    date_created = models.DateTimeField(auto_now_add = True)
    liked_by = models.ManyToManyField(MyUser, related_name = 'liked_by')

class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete = models.CASCADE, related_name='comments')
    user = models.ForeignKey(MyUser, on_delete = models.CASCADE)
    content = models.TextField()
    date_created = models.DateTimeField(auto_now_add = True)

class Notification(models.Model):
    user = models.ForeignKey(MyUser, on_delete = models.CASCADE, related_name = 'notifications')
    from_user = models.ForeignKey(MyUser, on_delete = models.CASCADE, related_name = 'notification_to')
    content = models.TextField()
    is_read = models.BooleanField(default = False)
    url = models.URLField(default = '/')

    def __str__(self):
        return self.user.profile_name

class ChatRoom(models.Model):
    users = models.ManyToManyField(MyUser, related_name='chat_rooms')
    notice_by_users = models.ManyToManyField(MyUser, related_name = 'chat_room_noticed')
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, verbose_name='UUID')
    is_group_chat = models.BooleanField(default = False)
    last_interaction = models.DateTimeField(auto_now_add=True)

class Message(models.Model):
    user = models.ForeignKey(MyUser, on_delete=models.CASCADE, related_name = 'messages')
    read_by_users = models.ManyToManyField(MyUser, related_name = 'read_messages')
    chat_room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE)
    date_created = models.DateTimeField(auto_now_add=True)
    content = models.TextField()
