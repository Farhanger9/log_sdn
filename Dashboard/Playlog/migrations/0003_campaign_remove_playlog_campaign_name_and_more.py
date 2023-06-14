# Generated by Django 4.2.1 on 2023-06-06 07:38

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('Playlog', '0002_playlog_created_at_playlog_updated_at_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Campaign',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(db_index=True, default=None, max_length=1024, null=True)),
            ],
        ),
        migrations.RemoveField(
            model_name='playlog',
            name='Campaign_Name',
        ),
        migrations.AddField(
            model_name='playlog',
            name='campaign',
            field=models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='playlogs', to='Playlog.campaign'),
        ),
    ]
