# Generated by Django 3.2 on 2023-06-10 14:16

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('tags', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='FavoriteRecipe',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
            options={
                'verbose_name': 'Ваш любимый рецепт',
                'verbose_name_plural': 'Ваши любимые рецепты',
            },
        ),
        migrations.CreateModel(
            name='IngredientInRecipe',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.PositiveSmallIntegerField(help_text='Введите количество ингредиентов', validators=[django.core.validators.MinValueValidator(1, message='Укажите количество ингредиентов (больше, или равное 1)')], verbose_name='Количество ингредиентов')),
            ],
            options={
                'verbose_name': 'Ингредиент рецепта',
                'verbose_name_plural': 'Ингредиенты рецептов',
            },
        ),
        migrations.CreateModel(
            name='Recipe',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True, help_text='Автоматически устанавливается текущая дата и время', verbose_name='Дата создания рецепта')),
                ('name', models.CharField(help_text='Введите, пожалуйста, название рецепта', max_length=200, verbose_name='Название рецепта')),
                ('image', models.ImageField(help_text='Добавьте, пожалуйста, картинку', upload_to='recipes/', verbose_name='Картинка')),
                ('text', models.TextField(help_text='Введите, пожалуйста, описание', verbose_name='Описание рецепта')),
                ('cooking_time', models.PositiveSmallIntegerField(help_text='Введите время приготовления в минутах', validators=[django.core.validators.MinValueValidator(1, message='Укажите время приготовления (больше, или равное 1)')], verbose_name='Время приготовления в минутах')),
            ],
            options={
                'verbose_name': 'Рецепт',
                'verbose_name_plural': 'Рецепты',
                'ordering': ('-created',),
                'default_related_name': '%(class)ss',
            },
        ),
        migrations.CreateModel(
            name='TagRecipe',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('recipe', models.ForeignKey(help_text='Выберите, пожалуйста, рецепт', on_delete=django.db.models.deletion.CASCADE, to='recipes.recipe', verbose_name='Рецепт')),
                ('tag', models.ForeignKey(help_text='Выберите, пожалуйста, тег из списка', on_delete=django.db.models.deletion.RESTRICT, to='tags.tag', verbose_name='Тег')),
            ],
            options={
                'verbose_name': 'Тег рецепта',
                'verbose_name_plural': 'Теги рецептов',
            },
        ),
        migrations.CreateModel(
            name='ShoppingCartRecipe',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('recipe', models.ForeignKey(help_text='Выберите, пожалуйста, рецепт', on_delete=django.db.models.deletion.CASCADE, to='recipes.recipe', verbose_name='Рецепт')),
            ],
            options={
                'verbose_name': 'Рецепт в корзине пользователя',
                'verbose_name_plural': 'Рецепты в корзинах пользователей',
            },
        ),
    ]
