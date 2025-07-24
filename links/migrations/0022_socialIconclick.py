# Generated manually for SocialIconClick model

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('links', '0021_analyticscache_linkclick_profileview'),
    ]

    operations = [
        migrations.CreateModel(
            name='SocialIconClick',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('ip_address', models.GenericIPAddressField(blank=True, null=True)),
                ('user_agent', models.TextField(blank=True)),
                ('referrer', models.URLField(blank=True, null=True)),
                ('device_type', models.CharField(blank=True, choices=[('mobile', 'Mobile'), ('desktop', 'Desktop'), ('tablet', 'Tablet')], max_length=20)),
                ('country', models.CharField(blank=True, max_length=100)),
                ('country_code', models.CharField(blank=True, max_length=2)),
                ('profile', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='all_social_clicks', to='links.profile')),
                ('social_icon', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='social_clicks', to='links.socialicon')),
            ],
            options={
                'ordering': ['-timestamp'],
                'indexes': [
                    models.Index(fields=['social_icon', '-timestamp'], name='links_socia_social__0b7e6c_idx'),
                    models.Index(fields=['profile', '-timestamp'], name='links_socia_profile_d4e3a7_idx'),
                    models.Index(fields=['timestamp'], name='links_socia_timesta_4f8c1a_idx'),
                ],
            },
        ),
    ]