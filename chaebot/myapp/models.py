from django.db import models


class FileUpload(models.Model):
    mp3_file = models.FileField(upload_to="mp3s/", null=True, blank=True)
    pdf_file = models.FileField(upload_to="pdfs/", null=True, blank=True)
    upload_date = models.DateTimeField(auto_now_add=True)
    processed_date = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"File uploaded on {self.upload_date.strftime('%Y-%m-%d %H:%M:%S')}"
