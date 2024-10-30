from departments.models.wrgl_file import WrglFile

def update_wrgl_file_urls(csv_slug: str, csv_url: str) -> bool:
    """
    Update the url and download_url fields of a WrglFile given its slug.
    
    Args:
        csv_slug: The slug of the WrglFile to update
        csv_url: The new URL to set for both url and download_url fields
        
    Returns:
        bool: True if update was successful, False if no matching record found
        
    Example:
        >>> update_wrgl_file_urls('my-csv-2023', 'https://example.com/file.csv')
        True
    """
    try:
        wrgl_file = WrglFile.objects.get(slug=csv_slug)
        wrgl_file.url = csv_url
        wrgl_file.download_url = csv_url
        wrgl_file.save()
        return True
    except WrglFile.DoesNotExist:
        return False
