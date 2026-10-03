from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

# Shared objects — created here so every module can import them
# without circular-import headaches.
db = SQLAlchemy()
migrate = Migrate()