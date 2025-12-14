# Generated migration for django_ip_access

from django.db import migrations, models
import django.core.validators


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='GrantedIP',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ip_address', models.CharField(help_text="IP address or CIDR range (e.g., '192.168.1.1' or '192.168.1.0/24')", max_length=50, validators=[django.core.validators.RegexValidator(message='Enter a valid IP address or CIDR range', regex='^[\\d\\./:]+$')])),
                ('description', models.TextField(blank=True, help_text='Optional description for this IP entry', null=True)),
                ('is_active', models.BooleanField(default=True, help_text='Whether this IP entry is active')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Granted IP',
                'verbose_name_plural': 'Granted IPs',
                'db_table': 'granted_ips',
            },
        ),
        migrations.AddIndex(
            model_name='grantedip',
            index=models.Index(fields=['ip_address', 'is_active'], name='django_ip_a_ip_add_123456_idx'),
        ),
    ]

