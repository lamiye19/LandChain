# Generated by Django 4.0.6 on 2022-08-05 15:03

import django.contrib.auth.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0002_alter_user_managers_alter_requisition_number_and_more'),
    ]

    operations = [
        migrations.AlterModelManagers(
            name='user',
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.RemoveField(
            model_name='requisition',
            name='nif',
        ),
        migrations.AlterField(
            model_name='complaint',
            name='proof_file',
            field=models.FileField(upload_to='plaintes/%Y/%m/%d/'),
        ),
        migrations.AlterField(
            model_name='requisition',
            name='authorization',
            field=models.FileField(blank=True, null=True, upload_to='requisition/%Y/%m/%d/'),
        ),
        migrations.AlterField(
            model_name='requisition',
            name='floor_plan',
            field=models.FileField(upload_to='requisition/%Y/%m/%d/'),
        ),
        migrations.AlterField(
            model_name='requisition',
            name='land_receipt',
            field=models.FileField(upload_to='requisition/%Y/%m/%d/'),
        ),
        migrations.AlterField(
            model_name='requisition',
            name='liquidation_receipt',
            field=models.FileField(blank=True, null=True, upload_to='requisition/%Y/%m/%d/'),
        ),
        migrations.AlterField(
            model_name='requisition',
            name='notarial_instrument',
            field=models.FileField(blank=True, null=True, upload_to='requisition/%Y/%m/%d/'),
        ),
        migrations.AlterField(
            model_name='requisition',
            name='number',
            field=models.BigIntegerField(default=1659711812, primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='requisition',
            name='pay',
            field=models.CharField(blank=True, max_length=30, null=True),
        ),
    ]
