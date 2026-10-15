from django.db import models


class Contact(models.Model):
    name = models.CharField("Имя", max_length=100)
    phone = models.CharField("Телефон", max_length=20)
    email = models.EmailField("Email")
    category = models.CharField("Категория", max_length=50)
    created_at = models.DateTimeField("Создан", auto_now_add=True)

    class Meta:
        verbose_name = "Контакт"
        verbose_name_plural = "Контакты"
        constraints = [
            models.UniqueConstraint(
                fields=["email", "phone"],
                name="unique_email_phone",
            )
        ]

    def __str__(self):
        return f"{self.name} <{self.email}>"