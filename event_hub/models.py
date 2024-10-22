from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models.signals import pre_save
from django.dispatch import receiver


class MyUser(AbstractUser):
    name = models.CharField(max_length=150, blank=False, null=False)
    email = models.EmailField(unique=True, blank=False, null=False)
    bio = models.CharField(max_length=300, blank=True, null=False)
    avatar = models.ImageField(upload_to='avatars', blank=True, null=False)

    USERNAME_FIELD = 'email'
    EMAIL_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'name']


# @receiver(pre_save, sender=MyUser)
# def test_f(sender, instance, **kwargs):
#     title = 'Join Us for the Annual Tech Innovations Conference 2024: Exploring the Future of Technology, Networking Opportunities, and Industry Insights in Mumbai'
#     print(slugify(title))
#     print(timezone.now().strftime('%Y%m%d%H%M%S'))
#     # print('This is pk', instance.pk)
#     # print(datetime.datetime.strptime(
#     #     '2024-09-29 18:13:50.201763', "%Y-%m-%d %H:%M:%S.%f"))
#     # print(pytz.timezone('Asia/Kolkata'))
#     # print(datetime.datetime.now())
#     # print(timezone.now())


class Tag(models.Model):
    name = models.CharField(
        max_length=20, unique=True,
        blank=False, null=False
    )

    def save(self, *args, **kwargs):
        self.name = self.name.lower()
        return super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f'{self.name}'


class Event(models.Model):
    title = models.CharField(max_length=150, blank=False, null=False)
    slug = models.SlugField(max_length=80, unique=True,
                            blank=True, null=False)
    description = models.TextField(blank=False, null=False)
    cover_image = models.ImageField(
        upload_to='event_images', blank=False, null=False)
    datetime = models.DateTimeField(blank=False, null=False)
    timezone = models.CharField(max_length=100, blank=True, null=False)
    address = models.CharField(max_length=150, blank=False, null=False)
    city = models.CharField(max_length=100, blank=False, null=False)
    pincode = models.CharField(max_length=15, blank=False, null=False)
    state = models.CharField(max_length=100, blank=False, null=False)
    country = models.CharField(max_length=150, blank=False, null=False)
    tags = models.ManyToManyField(Tag)
    organizer = models.ForeignKey(
        MyUser, on_delete=models.CASCADE, related_name='organized_events', null=False)
    created_at = models.DateTimeField(auto_now_add=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, blank=True)
