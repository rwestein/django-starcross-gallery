import django

from django.core.files import storage
from django.conf import settings as django_settings
try:
    from django.core.files.storage.handler import InvalidStorageError
except ModuleNotFoundError:
    # InvalidStorageError is not used when it's not available (for Django < 4.2),
    # so just ignore it.
    pass

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

    @classmethod
    def determine_storage(cls):
        storage_instance = cls.determine_post42_storage()
        if storage_instance is not None:
            return storage_instance
        storage_instance = cls.determine_pre42_storage()
        if storage_instance is not None:
            return storage_instance
        return storage.DefaultStorage()

    @classmethod
    def determine_thumbnail_storage(cls):
        storage_instance = cls.determine_post42_thumbnail_storage()
        if storage_instance is not None:
            return storage_instance
        storage_instance = cls.determine_pre42_thumbnail_storage()
        if storage_instance is not None:
            return storage_instance
        # If it's not set explicitly, fall back to the setting for regular
        # gallery storage
        return cls.determine_storage()


gallery_storage = StorageFactory.determine_storage()
gallery_thumbnail_storage = StorageFactory.determine_thumbnail_storage()
