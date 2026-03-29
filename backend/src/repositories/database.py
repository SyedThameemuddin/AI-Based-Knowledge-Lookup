from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import sessionmaker
from contextlib import contextmanager
from settings import config

class Database:
    
    _instance=None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Database, cls).__new__(cls)
            cls.engine = cls._create_engine()
            cls.SessionLocal = sessionmaker(
            bind=cls.engine,
            autoflush=False,
            autocommit=False
        )
        
        print(f"Singleton object: {cls._instance}")
        return cls._instance
    
    
    # def __init__(self):
    #     print("\n databse __init__")
    #     self.engine = self._create_engine()
    #     self.SessionLocal = sessionmaker(
    #         bind=self.engine,
    #         autoflush=False,
    #         autocommit=False
    #     )
    
    
    @classmethod
    def _create_engine(cls):
        db_url = (
            f"postgresql+psycopg2://{config.db_username}:"
            f"{config.db_password}@"
            f"{config.db_host}:"
            f"{config.db_port}/"
            f"{config.db_name}"
        )
        return create_engine(db_url)

    @contextmanager
    def get_db(self):
        
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    async def get_session(self):
        """
        Async generator if you need async routes (not used in this KB flow).
        """
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def inspector(self, engine=None):
        return inspect(engine or self.engine)

