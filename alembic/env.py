import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from app.db.base import Base

target_metadata = Base.metadata
