from django.db import models
from django.urls import reverse
from django.template.defaultfilters import slugify
from django.core.validators import MinLengthValidator, MaxLengthValidator
from django.contrib.auth import get_user_model
from django_redis import get_redis_connectioncd 


class PublishedManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_published=Women.Status.PUBLISHED)

class Women(models.Model):
    class Status(models.IntegerChoices):
        DRAFT = 0, 'chernovik'
        PUBLISHED = 1, 'opublicovano'


    title = models.CharField(max_length=255, verbose_name='Заголовок',)
    content = models.TextField(blank=True)
    slug = models.SlugField(max_length=255, unique=True, db_index=True, verbose_name='Slug', validators=[MinLengthValidator(5, message='Минимум 5 символов'), MaxLengthValidator(100, message='Максимум 100 символов')])
    photo = models.ImageField(upload_to="photos/%Y/%m/%d/", default=None, blank=True, null=True, verbose_name="Фото статьи")
    time_create = models.DateTimeField(auto_now_add=True, verbose_name='Время создания')
    time_update = models.DateTimeField(auto_now=True, verbose_name='Время изменения')
    is_published = models.BooleanField(choices=tuple(map(lambda x: (bool(x[0]), x[1]), Status.choices)), default=Status.DRAFT, verbose_name='Статус')

    cat = models.ForeignKey('Category', on_delete=models.PROTECT, null=True, related_name='posts', verbose_name='Категории')
    tags = models.ManyToManyField('TagPost', blank=True, related_name='tags', verbose_name='Теги')
    husband = models.OneToOneField('Husband', on_delete=models.SET_NULL, null=True, blank=True, related_name='wum', verbose_name='Муж')

    author = models.ForeignKey(get_user_model(), on_delete=models.SET_NULL, related_name='posts', null=True, default=None)

    objects = models.Manager()
    published = PublishedManager()
    redis_connection = get_redis_connection()

    def __str__(self):
        return self.title
    
    class Meta:
        verbose_name = "Известные женщины"
        verbose_name_plural = "Известные женщины"
        ordering = ['-time_create']
        indexes = [
            models.Index(fields=['-time_create'])
        ]
    def get_absolute_url(self):
        return reverse('post', kwargs={"post_slug": self.slug})

    # def save(self, *args, **kwargs):
    #     self.slug = slugify(self,title)
    #     super().save(*args, **kwargs)


class Category(models.Model):
    name = models.CharField(max_length=100, db_index=True, verbose_name="Категория")
    slug = models.SlugField(max_length=255, unique=True, db_index=True)
    
    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"

    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse("category", kwargs={"cat_slug": self.slug})

class TagPost(models.Model):
    tag = models.CharField(max_length=100, db_index=True)
    slug = models.SlugField(max_length=255, unique=True, db_index=True)
    
    def __str__(self):
        return self.tag
    
    def get_absolute_url(self):
        return reverse("tag", kwargs={"tag_slug": self.slug})

class Husband(models.Model):
    name = models.CharField(max_length=100,)
    age = models.IntegerField(null=True)

    def __str__(self):
        return self.name
    
class UploadFiles(models.Model):
    file = models.FileField(upload_to='uploads_model')

    