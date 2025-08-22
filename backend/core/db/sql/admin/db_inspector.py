from sqlalchemy import create_engine, inspect
from core.config import settings
from core.db.sql.base_class import Base
from core.db.sql.init_sql_all_models import load_all_models

def get_sql_db_status():
    """
    Inspecciona la base de datos y la compara con los modelos definidos en el código.
    """
    load_all_models()
    models_in_code = set(Base.metadata.tables.keys())
    
    engine = create_engine(str(settings.DATABASE_URL))
    inspector = inspect(engine)
    tables_in_db = set(inspector.get_table_names())
    engine.dispose()
    
    synced_models = models_in_code.intersection(tables_in_db)
    code_only_models = models_in_code.difference(tables_in_db)
    db_only_tables = tables_in_db.difference(models_in_code)
    
    return {
        "synced": sorted(list(synced_models)),
        "code_only": sorted(list(code_only_models)),
        "db_only": sorted(list(db_only_tables)),
    }