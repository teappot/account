import os, uuid
import re
from django.core.paginator import Paginator
from django.db import models
from teacore.models import ImageHelper, Lang, TeaModelAbstract
from django.utils import timezone
from django.utils.text import slugify
from datetime import timedelta
from django.contrib.auth.models import User
from django.conf import settings
from django.template import engines
from django.contrib.auth.models import AbstractUser

class TeaAccountAbstract(TeaModelAbstract):

    IMAGEPATH = "account/"
    VIEWNAME = "account:user"
    PAGE = 1

    lang = models.ForeignKey(Lang, on_delete=models.CASCADE, default=1)
    timezone = models.CharField(max_length=10, default="GMT")

    image = models.ImageField(upload_to=ImageHelper.rename_to_uuid, blank=True, null=True, default=None)

    @classmethod
    def get(cls, description_class, slug, lang, page=1, is_published=True):

        user_description = description_class.objects.filter(
            user__slug=slug, 
            is_published=is_published,
            lang__code=lang
        ).first()

        if user_description is None and re.match(r'^[\da-f]{8}-([\da-f]{4}-){3}[\da-f]{12}$', str(slug).lower()):
            user_description = description_class.objects.filter(
                author__uuid=slug, 
                is_published=is_published,
                lang__code=lang
            ).first()

        if user_description is not None:
            user_description.user.PAGE = page

            user_description.user.fullname = " ".join([
                user_description.user.user.first_name, 
                user_description.user.user.last_name
            ])
            
            for attr in ['lang', 'keywords', 'description', 'body', 'is_published', 'is_public']:
                setattr(user_description.user, attr, getattr(user_description, attr))

            # Para renderizar widgets en el body
            user_description.body = engines['django'].from_string("\n".join([
                "{% load static %}", 
                "{% load i18n %}", 
                "{% load widget %}", 
                user_description.body
            ])).render({})

            return user_description.user
        
        return None

    @classmethod
    def list(cls, descrption_class, lang, page=1, is_published=True):
        user_descriptions = descrption_class.objects.filter(lang__code=lang, is_published=is_published)
        paginator = Paginator(user_descriptions, settings.USER_PAGINATION)
        users = paginator.get_page(page)

        for user_description in users:
            for attr in ['slug', 'image']:
                setattr(user_description, attr, getattr(user_description.user, attr))
            
            user_description.VIEWNAME = cls.VIEWNAME #reverse(cls.VIEWNAME, args=[author_description.slug])
            user_description.fullname = " ".join([
                user_description.user.user.first_name, 
                user_description.user.user.last_name
            ])
            user_description.title = user_description.fullname
        
        return users
    
    def save(self, *args, **kwargs):
        #self.slug = slugify("-".join([self.user.first_name, self.user.last_name])).lower()
        #if not self.slug:
        #    self.slug = self.uuid
        
        super().save(*args, **kwargs)
    
    def delete(self, *args, **kwargs):
        previous = type(self).objects.get(pk=self.pk)
        filepath = os.path.join(settings.MEDIA_ROOT, previous.image.name)
        if os.path.isfile(filepath):
            os.remove(filepath)

        return super().delete(*args, **kwargs)
    
    class Meta:
        abstract = True

    def __str__(self):
        return self.user.username

class UserDescriptionAbstract(models.Model):

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    lang = models.ForeignKey(Lang, on_delete=models.CASCADE, default=1)

    keywords = models.CharField(max_length=32, blank=True, default="")       # SEO: META_KEYWORDS / schema: None
    description = models.CharField(max_length=155, blank=True, default="")   # SEO: META_DESCRIPTION / schema: None
    noindex = models.BooleanField(default=False)
    nofollow = models.BooleanField(default=False)    

    body = models.TextField(help_text="Markdown", blank=True, default="")
    
    is_published = models.BooleanField(default=False)
    is_public = models.BooleanField(default=False)

    @classmethod
    def get(cls, user, lang):
        raise NotImplementedError('`get(user, lang)` must be implemented.')
    
    class Meta:
        abstract = True
        verbose_name_plural = "User Descriptions"
        constraints = [
            models.UniqueConstraint(fields=['user', 'lang'], name='user_description_abstract_unique_user_lang')
        ]

class UserTaskToken(models.Model):

    TASK_CHOICES = [
        ("RECOVERY", "Recovery"),
    ]

    STATE_CHOICES = [
        ("ACTIVE", "Active"),
        ("USED", "Used"),
        ("EXPIRED", "Expired"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='users')
    token = models.UUIDField(default=uuid.uuid4, editable=False, null=False, unique=True)

    task = models.CharField(max_length=32, choices=TASK_CHOICES, null=False)
    state = models.CharField(max_length=32, choices=STATE_CHOICES, null=False, default="ACTIVE")

    expires_at = models.DateTimeField()

    def use_recovery_token(self, password_new):

        if settings.AUTH_EMAIL_AS_USERNAME:
            try:
                self.user = User.objects.get(username=self.user.email)
            except Exception:
                self.user.username = self.user.email.lower()

        self.user.set_password(password_new)
        self.user.save()

        self.state = "USED"
        self.save()
    
    @classmethod
    def get_recovery_token(cls, username, token):
        return cls.__get_token(username, token, "RECOVERY")
    
    @classmethod
    def __get_token(cls, username, token, task):
        rows = cls.objects.filter(user__username=username, task=task, state="ACTIVE")
        rows.filter(expires_at__lt=timezone.now()).update(state="EXPIRED")

        return rows.filter(token=token).first()
    
    @classmethod
    def new_recovery_token(cls, username):
        user = User.objects.get(username=username)
        return cls.__new_token(user, "RECOVERY")

    @classmethod 
    def __new_token(cls, user, task):
        cls.objects.filter(user=user, task=task, state = "ACTIVE").update(state="EXPIRED")
        return cls.objects.create(
            user = user,
            task = task,
            state = "ACTIVE"
        )

    def __str__(self):
        return f"{self.user.username} - {self.state}"
    
    def save(self, *args, **kwargs):
        if not self.id:  # Solo si es un nuevo objeto (no una actualización)
            self.expires_at = timezone.now() + timedelta(minutes=settings.AUTH_TASK_TOKEN_LIFETIME)
        
        super().save(*args, **kwargs)
