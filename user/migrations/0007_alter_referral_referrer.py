# Generated by Django 5.1.5 on 2025-02-25 11:26

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0006_remove_player_predict_slot_slot'),
    ]

    operations = [
        migrations.AlterField(
            model_name='referral',
            name='referrer',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='refers', to='user.player'),
        ),
    ]
