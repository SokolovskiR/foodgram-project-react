# Generated by Django 3.2.13 on 2022-05-13 14:24

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('foodgram', '0003_alter_ingredientamount_amount'),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name='subscription',
            name='unique_following',
        ),
        migrations.AddField(
            model_name='subscription',
            name='following',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='foodgram_subscription_following', to='users.user'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='subscription',
            name='author',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='foodgram_subscription_authors', to=settings.AUTH_USER_MODEL, verbose_name='Автор'),
        ),
        migrations.AddConstraint(
            model_name='subscription',
            constraint=models.UniqueConstraint(fields=('user', 'following'), name='unique_following'),
        ),
    ]
