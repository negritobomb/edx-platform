from ratelimitbackend import admin
from config_models.admin import ConfigurationModelAdmin
from verify_student.models import (
    SoftwareSecurePhotoVerification,
    InCourseReverificationConfiguration,
    VerificationStatus,
    SkippedReverification,
)


class SoftwareSecurePhotoVerificationAdmin(admin.ModelAdmin):
    """
    Admin for the SoftwareSecurePhotoVerification table.
    """
    list_display = ('id', 'user', 'status', 'receipt_id', 'submitted_at', 'updated_at')
    exclude = ('window',)   # TODO: Remove after deleting this field from the model.
    search_fields = (
        'receipt_id',
    )


class VerificationStatusAdmin(admin.ModelAdmin):
    """
    Admin for the VerificationStatus table.
    """
    list_display = ('timestamp', 'user', 'status', 'checkpoint')
    readonly_fields = ()
    search_fields = ('checkpoint__checkpoint_location', 'user__username')

    def get_readonly_fields(self, request, obj=None):
        """When editing an existing record, all fields should be read-only.

        VerificationStatus records should be immutable; to change the user's
        status, create a new record with the updated status and a more
        recent timestamp.

        """
        if obj:
            return self.readonly_fields + ('status', 'checkpoint', 'user', 'response', 'error')
        return self.readonly_fields

    def has_delete_permission(self, request, obj=None):
        """The verification status table is append-only. """
        return False


class SkippedReverificationAdmin(admin.ModelAdmin):
    """Admin for the SkippedReverification table. """
    list_display = ('created_at', 'user', 'course_id', 'checkpoint')
    readonly_fields = ('user', 'course_id')
    search_fields = ('user__username', 'course_id', 'checkpoint__checkpoint_location')

    def has_add_permission(self, request):
        """Skipped verifications can't be created in Django admin. """
        return False


admin.site.register(SoftwareSecurePhotoVerification, SoftwareSecurePhotoVerificationAdmin)
admin.site.register(InCourseReverificationConfiguration, ConfigurationModelAdmin)
admin.site.register(SkippedReverification, SkippedReverificationAdmin)
admin.site.register(VerificationStatus, VerificationStatusAdmin)
