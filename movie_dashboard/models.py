from django.db import models

# Create your models here.

class Movie(models.Model):
    title = models.CharField(max_length=200, verbose_name='电影名称')
    release_date = models.DateField(verbose_name='上映日期')
    budget = models.BigIntegerField(verbose_name='预算（美元）')
    revenue = models.BigIntegerField(verbose_name='票房（美元）')
    runtime = models.IntegerField(verbose_name='片长（分钟）')
    vote_average = models.FloatField(verbose_name='平均评分')
    vote_count = models.IntegerField(verbose_name='评分数量')
    overview = models.TextField(verbose_name='剧情简介')
    poster_path = models.CharField(max_length=200, verbose_name='海报路径')
    
    class Meta:
        verbose_name = '电影'
        verbose_name_plural = verbose_name
        
    def __str__(self):
        return self.title

class Genre(models.Model):
    name = models.CharField(max_length=50, verbose_name='类型名称')
    movies = models.ManyToManyField(Movie, related_name='genres')
    
    class Meta:
        verbose_name = '电影类型'
        verbose_name_plural = verbose_name
        
    def __str__(self):
        return self.name

class Director(models.Model):
    name = models.CharField(max_length=100, verbose_name='导演姓名')
    movies = models.ManyToManyField(Movie, related_name='directors')
    
    class Meta:
        verbose_name = '导演'
        verbose_name_plural = verbose_name
        
    def __str__(self):
        return self.name

class Actor(models.Model):
    name = models.CharField(max_length=100, verbose_name='演员姓名')
    movies = models.ManyToManyField(Movie, related_name='actors')
    
    class Meta:
        verbose_name = '演员'
        verbose_name_plural = verbose_name
        
    def __str__(self):
        return self.name

class ProductionCompany(models.Model):
    name = models.CharField(max_length=200, verbose_name='制作公司')
    country = models.CharField(max_length=100, verbose_name='国家')
    movies = models.ManyToManyField(Movie, related_name='production_companies')
    
    class Meta:
        verbose_name = '制作公司'
        verbose_name_plural = verbose_name
        
    def __str__(self):
        return self.name
