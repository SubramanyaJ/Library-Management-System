# Generated by Django 5.1.3 on 2024-11-27 02:29

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('libraryweb', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='LibraryUser',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('lib_num', models.CharField(max_length=15, unique=True)),
                ('is_active', models.BooleanField(default=False)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='library_profile', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.DeleteModel(
            name='LibNumCounter',
        ),
        migrations.AlterField(
            model_name='rating',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ratings', to='libraryweb.libraryuser'),
        ),
        migrations.AlterField(
            model_name='request',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='book_requests', to='libraryweb.libraryuser'),
        ),
        migrations.AlterField(
            model_name='userborrowed',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='borrowed_books', to='libraryweb.libraryuser'),
        ),
        migrations.DeleteModel(
            name='User',
        ),
    ]
