from django.conf import settings


def url_prefix(request):
    """
    Context processor to make URL_PREFIX available in all templates.
    This allows templates to dynamically use the correct URL prefix
    based on the deployment branch (e.g., /planer/, /planer-dev/, etc.)
    """
    return {"URL_PREFIX": getattr(settings, "URL_PREFIX", "planer")}
