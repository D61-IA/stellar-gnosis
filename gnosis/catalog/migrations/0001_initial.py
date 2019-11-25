# Generated by Django 2.2.5 on 2019-11-24 06:29

import catalog.models
import datetime
from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Collection',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('description', models.TextField(blank=True, null=True)),
                ('keywords', models.CharField(blank=True, max_length=100, null=True)),
                ('created_at', models.DateField(auto_now_add=True)),
                ('updated_at', models.DateField(null=True)),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='collections', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['name', '-created_at'],
            },
        ),
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.TextField()),
                ('created_at', models.DateField(auto_now_add=True)),
                ('updated_at', models.DateField(null=True)),
                ('is_flagged', models.BooleanField(default=False)),
                ('is_hidden', models.BooleanField(default=False)),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='author', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['created_at'],
            },
        ),
        migrations.CreateModel(
            name='Dataset',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=300)),
                ('keywords', models.CharField(max_length=300)),
                ('description', models.TextField()),
                ('publication_year', models.SmallIntegerField(validators=[django.core.validators.MaxValueValidator(2020), django.core.validators.MinValueValidator(1900)])),
                ('publication_month', models.CharField(blank=True, choices=[('January', 'January'), ('February', 'February'), ('March', 'March'), ('April', 'April'), ('May', 'May'), ('June', 'June'), ('July', 'July'), ('August', 'August'), ('September', 'September'), ('October', 'October'), ('November', 'November'), ('December', 'December')], max_length=25)),
                ('dataset_type', models.CharField(choices=[('Network', 'Network'), ('Image(s)', 'Image(s)'), ('Video(s)', 'Video(s)'), ('Audio', 'Audio'), ('Biology', 'Biology'), ('Chemistry', 'Chemistry'), ('Astronomy', 'Astronomy'), ('Physics', 'Physics'), ('Other', 'Other')], max_length=50)),
                ('website', models.CharField(max_length=2000, validators=[django.core.validators.URLValidator()])),
                ('created_at', models.DateField(auto_now_add=True)),
                ('updated_at', models.DateField(null=True)),
                ('created_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['name', 'publication_year', 'dataset_type'],
            },
        ),
        migrations.CreateModel(
            name='Paper',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=500)),
                ('abstract', models.TextField()),
                ('keywords', models.CharField(blank=True, max_length=125)),
                ('download_link', models.CharField(max_length=2000, validators=[django.core.validators.URLValidator()])),
                ('is_public', models.BooleanField(default=True)),
                ('source_link', models.CharField(blank=True, max_length=250)),
                ('created_at', models.DateField(auto_now_add=True)),
                ('updated_at', models.DateField(null=True)),
                ('created_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='papers_added', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['title', '-created_at'],
            },
        ),
        migrations.CreateModel(
            name='PaperAuthorRelationshipData',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order', models.SmallIntegerField(default=1, validators=[django.core.validators.MaxValueValidator(40), django.core.validators.MinValueValidator(1)])),
            ],
        ),
        migrations.CreateModel(
            name='ReadingGroup',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('description', models.TextField()),
                ('keywords', models.CharField(max_length=100)),
                ('is_public', models.BooleanField(default=False)),
                ('created_at', models.DateField(auto_now_add=True)),
                ('updated_at', models.DateField(null=True)),
            ],
            options={
                'ordering': ['name', '-created_at'],
            },
        ),
        migrations.CreateModel(
            name='Venue',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=250)),
                ('publication_year', models.SmallIntegerField(validators=[django.core.validators.MaxValueValidator(2020), django.core.validators.MinValueValidator(1900)])),
                ('publication_month', models.CharField(choices=[('January', 'January'), ('February', 'February'), ('March', 'March'), ('April', 'April'), ('May', 'May'), ('June', 'June'), ('July', 'July'), ('August', 'August'), ('September', 'September'), ('October', 'October'), ('November', 'November'), ('December', 'December')], max_length=25)),
                ('venue_type', models.CharField(choices=[('Journal', 'Journal'), ('Conference', 'Conference'), ('Workshop', 'Workshop'), ('Open Source', 'Open Source'), ('Tech Report', 'Tech Report'), ('Other', 'Other')], max_length=50)),
                ('publisher', models.CharField(blank=True, max_length=250)),
                ('keywords', models.CharField(max_length=250)),
                ('peer_reviewed', models.CharField(choices=[('Yes', 'Yes'), ('No', 'No')], max_length=15)),
                ('website', models.CharField(max_length=2000, validators=[django.core.validators.URLValidator()])),
                ('created_at', models.DateField(auto_now_add=True)),
                ('updated_at', models.DateField(null=True)),
                ('created_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='venue', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['name', 'publication_year', 'publication_month', 'venue_type'],
            },
        ),
        migrations.CreateModel(
            name='ReadingGroupMember',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('access_type', models.CharField(choices=[('granted', 'granted'), ('requested', 'requested'), ('banned', 'banned'), ('none', 'none')], max_length=50)),
                ('created_at', models.DateField(auto_now_add=True)),
                ('updated_at', models.DateField(null=True)),
                ('member', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='ReadingGroupEntry',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_discussed', models.DateField(blank=True, null=True)),
                ('date_proposed', models.DateField(auto_now_add=True)),
                ('paper', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='groups', to='catalog.Paper')),
                ('proposed_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='papers', to=settings.AUTH_USER_MODEL)),
                ('reading_group', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='papers', to='catalog.ReadingGroup')),
            ],
        ),
        migrations.AddField(
            model_name='readinggroup',
            name='members',
            field=models.ManyToManyField(to='catalog.ReadingGroupMember'),
        ),
        migrations.AddField(
            model_name='readinggroup',
            name='owner',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='reading_groups', to=settings.AUTH_USER_MODEL),
        ),
        migrations.CreateModel(
            name='Person',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(max_length=100)),
                ('last_name', models.CharField(max_length=100)),
                ('middle_name', models.CharField(blank=True, max_length=100, null=True)),
                ('affiliation', models.CharField(blank=True, max_length=250, null=True)),
                ('website', models.URLField(blank=True, max_length=500, null=True)),
                ('created_at', models.DateField(auto_now_add=True)),
                ('updated_at', models.DateField(null=True)),
                ('created_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='person', to=settings.AUTH_USER_MODEL)),
                ('papers', models.ManyToManyField(blank=True, through='catalog.PaperAuthorRelationshipData', to='catalog.Paper')),
            ],
            options={
                'ordering': ['last_name', 'first_name', 'affiliation'],
            },
        ),
        migrations.CreateModel(
            name='PaperRelationshipType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('relationship_type', models.CharField(choices=[('cites', 'cites'), ('uses', 'uses'), ('extends', 'extends')], max_length=25)),
                ('created_at', models.DateField(default=datetime.date.today)),
                ('updated_at', models.DateField(null=True)),
                ('paper_from', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='paper_from', to='catalog.Paper')),
                ('paper_to', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='paper_to', to='catalog.Paper')),
            ],
        ),
        migrations.CreateModel(
            name='PaperDatasetRelationshipData',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateField(auto_now_add=True)),
                ('updated_at', models.DateField(null=True)),
                ('dataset', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='dataset', to='catalog.Dataset')),
                ('from_paper', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='from_paper', to='catalog.Paper')),
            ],
        ),
        migrations.AddField(
            model_name='paperauthorrelationshipdata',
            name='author',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='author', to='catalog.Person'),
        ),
        migrations.AddField(
            model_name='paperauthorrelationshipdata',
            name='paper',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='source_paper', to='catalog.Paper'),
        ),
        migrations.AddField(
            model_name='paper',
            name='papers',
            field=models.ManyToManyField(blank=True, through='catalog.PaperRelationshipType', to='catalog.Paper'),
        ),
        migrations.AddField(
            model_name='paper',
            name='was_published_at',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='catalog.Venue'),
        ),
        migrations.CreateModel(
            name='Endorsement',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateField(auto_now_add=True)),
                ('paper', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='endorsements', to='catalog.Paper')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='endorsements', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
        migrations.AddField(
            model_name='dataset',
            name='papers',
            field=models.ManyToManyField(blank=True, through='catalog.PaperDatasetRelationshipData', to='catalog.Paper'),
        ),
        migrations.CreateModel(
            name='CommentFlag',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('violation', models.CharField(choices=[('spam', 'spam'), ('offensive', 'offensive'), ('pornography', 'pornography'), ('extremist', 'extremist'), ('violence', 'violence')], max_length=50)),
                ('description', models.TextField()),
                ('created_at', models.DateField(auto_now_add=True)),
                ('comment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='catalog.Comment')),
                ('proposed_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='comment_flags', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'comment flag',
                'ordering': ['violation', '-created_at'],
            },
        ),
        migrations.AddField(
            model_name='comment',
            name='paper',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='catalog.Paper'),
        ),
        migrations.CreateModel(
            name='CollectionEntry',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateField(auto_now_add=True)),
                ('collection', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='papers', to='catalog.Collection')),
                ('paper', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='collections', to='catalog.Paper')),
            ],
        ),
        migrations.CreateModel(
            name='Code',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('description', models.TextField()),
                ('website', models.CharField(max_length=2000, validators=[django.core.validators.URLValidator(), catalog.models.valid_code_website])),
                ('keywords', models.CharField(max_length=250)),
                ('created_at', models.DateField(auto_now_add=True)),
                ('updated_at', models.DateField(null=True)),
                ('created_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='codes_added', to=settings.AUTH_USER_MODEL)),
                ('papers', models.ManyToManyField(to='catalog.Paper')),
            ],
            options={
                'ordering': ['name', 'website', 'description', 'keywords'],
            },
        ),
    ]
