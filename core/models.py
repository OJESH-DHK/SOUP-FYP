import uuid
from django.db import models
from django.utils import timezone

class CommonModel(models.Model):
    """
    Abstract Base Model for the entire project.
    Provides: UUID primary keys, timestamps, and soft-delete capabilities.
    """
    # 1. Identity: UUIDs are more secure than auto-incrementing integers
    id = models.UUIDField(
        primary_key=True, 
        default=uuid.uuid4, 
        editable=False
    )

    # 2. Audit Timestamps
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    # 3. Soft Delete: Prevents accidental permanent data loss
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)

    # 4. Status Tracking: Useful for almost any entity (Active, Inactive, etc.)
    is_active = models.BooleanField(default=True)

    class Meta:
        abstract = True # Tells Django not to create a database table for this
        ordering = ['-created_at']

    def delete(self, soft=True, *args, **kwargs):
        """Override delete for soft-delete functionality by default."""
        if soft:
            self.is_deleted = True
            self.deleted_at = timezone.now()
            self.save()
        else:
            super().delete(*args, **kwargs)

    def restore(self):
        """Restore a soft-deleted item."""
        self.is_deleted = False
        self.deleted_at = None
        self.save()


