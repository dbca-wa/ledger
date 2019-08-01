class FdwManagerRouter:
    """
    A router to control all database operations on tables connected to the
    foreign data wrapper manager database defined by FDW_MANAGER_DATABASE_URL.
    """
    def db_for_read(self, model, **hints):
        """
        Attempts to read fdw_manager models go to fdw_manager_db.
        """
        if model._meta.app_label == 'fdw_manager':
            return 'fdw_manager_db'
        return None