def update_wrgl_urls(csv_slug, csv_url):
    """
    Updates both the url and download_url fields of a WrglFile record that matches the given slug.
    
    Parameters:
    -----------
    csv_slug : str
        The unique slug identifier of the WrglFile record to update
        Example: 'new-orleans-pd-2023'
    
    csv_url : str
        The new URL to set for both the url and download_url fields
        Example: 'https://storage.googleapis.com/bucket/file.csv'
    
    Database Table:
    --------------
    Table name: departments_wrglfile
    Relevant columns:
        - slug (CharField, unique=True)
        - url (CharField)
        - download_url (CharField)
    
    SQL Executed:
    ------------
    UPDATE departments_wrglfile 
    SET url = %(csv_url)s, download_url = %(csv_url)s 
    WHERE slug = %(csv_slug)s
    RETURNING id;
    
    Returns:
    --------
    bool
        True if a record was found and updated
        False if no matching record was found
    
    Example:
    --------
    >>> update_wrgl_urls('new-orleans-pd-2023', 'https://storage.googleapis.com/bucket/file.csv')
    True  # If record was found and updated
    False # If no record with that slug exists
    """
    conn = psycopg2.connect(
        dbname=os.environ['POSTGRES_DB'],
        user=os.environ['POSTGRES_USER'],
        password=os.environ['POSTGRES_PASSWORD'],
        host='localhost',  # Points to Cloud SQL Proxy
        port=5432
    )
    try:
        with conn.cursor() as cur:
            # Execute UPDATE query and return the id if successful
            cur.execute("""
                UPDATE departments_wrglfile 
                SET url = %s, download_url = %s 
                WHERE slug = %s
                RETURNING id
            """, (csv_url, csv_url, csv_slug))
            
            # fetchone() returns None if no rows were updated
            updated = cur.fetchone()
            
            # Commit the transaction
            conn.commit()
            
            # Return True if a row was updated, False otherwise
            return bool(updated)
    finally:
        # Always close the connection
        conn.close()
