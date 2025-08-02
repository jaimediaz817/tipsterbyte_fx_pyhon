from sqlalchemy.orm import declarative_base

# Esta es la instancia Base que TODOS tus modelos SQL en todos los subsistemas importarán y usarán.
Base = declarative_base()