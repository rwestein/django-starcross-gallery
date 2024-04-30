import django

from django.core.files import storage
from django.conf import settings as django_settings
from django.core.files.storage.handler import InvalidStorageError


# Create storage class and instance, based on the GALLERY_STORAGE setting
# This allows the user the flexibility to use Amazon S3 or any other object storage
# provider. Default is local file storage.

class StorageFactory:
    @staticmethod
    def determine_pre42_storage():
        try:
            return storage.get_storage_class(django_settings.GALLERY_STORAGE)()
        except AttributeError:
            pass

    @staticmethod
    def determine_post42_storage():
        if django.VERSION < (4, 2):
            return
        try:
            return storage.storages['gallery']
        except InvalidStorageError:
            pass

    @staticmethod
    def determine_pre42_thumbnail_storage():
        try:
            return storage.get_storage_class(django_settings.GALLERY_THUMBNAIL_STORAGE)()
        except AttributeError:
            pass

    @staticmethod
    def determine_post42_thumbnail_storage():
        if django.VERSION < (4, 2):
            return
        try:
            return storage.storages['gallery_thumbnails']
        except InvalidStorageError:
            pass

    def determine_storage(self):
        storage_instance = self.determine_post42_storage()
        if storage_instance is not None:
            return storage_instance
        storage_instance = self.determine_pre42_storage()
        if storage_instance is not None:
            return storage_instance
        return storage.DefaultStorage()

    def determine_thumbnail_storage(self):
        storage_instance = self.determine_post42_thumbnail_storage()
        if storage_instance is not None:
            return storage_instance
        storage_instance = self.determine_pre42_thumbnail_storage()
        if storage_instance is not None:
            return storage_instance
        # If it's not set explicitly, fall back to the setting for regular
        # gallery storage
        return self.determine_storage()


gallery_storage = StorageFactory().determine_storage()
gallery_thumbnail_storage = StorageFactory().determine_thumbnail_storage()
