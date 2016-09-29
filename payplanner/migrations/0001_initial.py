# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='BudgetData',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('itemAmmount', models.DecimalField(verbose_name=b'Amount', max_digits=8, decimal_places=2)),
                ('effectiveDate', models.DateField(default=datetime.date.today)),
                ('itemNote', models.CharField(max_length=400, verbose_name=b'Notes', blank=True)),
            ],
            options={
                'verbose_name_plural': 'Budget Data',
            },
        ),
        migrations.CreateModel(
            name='Categories',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('catName', models.CharField(unique=True, max_length=150, verbose_name=b'Category')),
                ('catDes', models.CharField(unique=True, max_length=500, verbose_name=b'Description')),
            ],
            options={
                'verbose_name_plural': 'Expense/Income Categories',
            },
        ),
        migrations.CreateModel(
            name='Cycles',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('cycleName', models.CharField(unique=True, max_length=150, verbose_name=b'Name')),
                ('cycleLength', models.IntegerField(verbose_name=b'Length of Cycle(Days)')),
            ],
            options={
                'verbose_name_plural': 'Pay Cycles',
            },
        ),
        migrations.CreateModel(
            name='Items',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('itemName', models.CharField(max_length=150, verbose_name=b'Name')),
                ('itemType', models.CharField(max_length=20, verbose_name=b'Item Type', blank=True)),
                ('itemAmount', models.DecimalField(verbose_name=b'Amount Due', max_digits=6, decimal_places=2)),
                ('nextDueDate', models.DateField(default=datetime.date.today, verbose_name=b'Next Due Date')),
                ('endDate', models.DateField(null=True, verbose_name=b'End Date', blank=True)),
                ('skiplst', models.TextField(null=True, blank=True)),
                ('itemNote', models.CharField(max_length=400, verbose_name=b'Notes', blank=True)),
                ('category', models.ForeignKey(to_field=b'catName', blank=True, to='payplanner.Categories', null=True)),
                ('payCycle', models.ForeignKey(to='payplanner.Cycles', to_field=b'cycleName', verbose_name=b'Pay Cycle')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name_plural': 'Income/Expenses',
            },
        ),
        migrations.AddField(
            model_name='budgetdata',
            name='parentItem',
            field=models.ForeignKey(to='payplanner.Items'),
        ),
    ]
