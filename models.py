
  
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.core.validators import RegexValidator
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.urls import reverse
from django.utils import timezone
from django.utils.text import slugify
from hitcount.models import HitCountMixin, HitCount
from django.contrib.contenttypes.fields import GenericRelation

def upload_location(instance, filename, *args, **kwargs):
    file_path = 'blog/{author_id}/{title}-{filename}'.format(author_id=str(instance.author.id), title=str(instance.title), filename=filename
        )
    return file_path

class UserManager(BaseUserManager):
    """Define a model manager for User model with no username field."""

    use_in_migrations = True

    def _create_user(self, phone, password, **extra_fields):
        """Create and save a User with the given phone and password."""
        if not phone:
            raise ValueError('User must have phone number')
        phone = phone
        user = self.model(phone=phone, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, phone, password=None, **extra_fields):
        """Create and save a regular User with the given phone and password."""
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)

        return self._create_user(phone, password, **extra_fields)

    def create_superuser(self, phone, password, **extra_fields):
        """Create and save a SuperUser with the given phone and password."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(phone, password, **extra_fields)

class User(AbstractUser):
    """User model."""

    username = None
    name=models.CharField(max_length=50)
    email = models.EmailField(blank=True, null=True)
    phone_regex = RegexValidator(regex=r'(0/91)?[7-9][0-9]{9}', message="Phone number must be entered in the format: '+999999999'. Up to 12 digits allowed.")
    phone = models.CharField(_('phone number'), validators=[phone_regex], max_length=17, unique=True) # validators should be a list
    friends=models.ManyToManyField('User', blank=True)

    USERNAME_FIELD = 'phone'
    REQUIRED_FIELDS = ['email','name']

    objects = UserManager()
    def __str__(self):
        return self.name


class FriendRequest(models.Model):
    from_user = models.ForeignKey(User,related_name="from_user", on_delete=models.CASCADE)
    to_user = models.ForeignKey(User,related_name="to_user", on_delete=models.CASCADE)
    
    def __str__(self):
        return f"{self.from_user}-->>{self.to_user}"




class Post(models.Model):
    title=models.CharField(max_length=300)
    slug     = models.CharField(max_length=300, unique=True)
    content=models.TextField()
    image=models.ImageField(upload_to=upload_location, null=True, blank=True)
    author=models.ForeignKey(User, on_delete=models.CASCADE)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)
    hit_count_generic = GenericRelation(HitCount, object_id_field='object_pk',
     related_query_name='hit_count_generic_relation')
    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("post_detail", args=[self.created_at.year,
                    self.created_at.month,
                    self.created_at.day,
                    self.slug,
                    ]
        )


    def save(self, *args, **kwargs):
        self.slug = '-'.join((slugify(self.title), slugify(self.author)))
        super(Post, self).save(*args, **kwargs)