from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('system', '0006_notice_remove_users_groups_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name="SystemNotice",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "remark",
                    models.CharField(
                        blank=True,
                        max_length=255,
                        null=True,
                        verbose_name="描述",
                    ),
                ),
                (
                    "creator_id",
                    models.BigIntegerField(
                        blank=True,
                        null=True,
                        verbose_name="创建人",
                    ),
                ),
                (
                    "modifier",
                    models.CharField(
                        blank=True,
                        max_length=255,
                        null=True,
                        verbose_name="修改人",
                    ),
                ),
                (
                    "belong_dept",
                    models.IntegerField(
                        blank=True,
                        null=True,
                        verbose_name="数据归属部门",
                    ),
                ),
                (
                    "update_datetime",
                    models.DateTimeField(
                        blank=True,
                        null=True,
                        verbose_name="修改时间",
                    ),
                ),
                (
                    "create_datetime",
                    models.DateTimeField(
                        blank=True,
                        null=True,
                        verbose_name="创建时间",
                    ),
                ),
                (
                    "sort",
                    models.IntegerField(
                        blank=True,
                        default=0,
                        null=True,
                        verbose_name="排序",
                    ),
                ),
                (
                    "title",
                    models.CharField(
                        blank=True,
                        max_length=255,
                        null=True,
                        verbose_name="标题",
                    ),
                ),
                (
                    "content",
                    models.TextField(
                        blank=True,
                        null=True,
                        verbose_name="内容",
                    ),
                ),
                (
                    "status",
                    models.BooleanField(
                        default=False,
                        verbose_name="状态",
                    ),
                ),
            ],
            options={
                "verbose_name": "公告管理",
                "verbose_name_plural": "公告管理",
                "db_table": "system_notice",
                "ordering": ["sort"],
            },
        ),
        migrations.AddIndex(
            model_name="notice",
            index=models.Index(
                fields=["creator_id"],
                name="system_notice_creator_id_idx",
            ),
        ),
    ]