from celery import Celery # type: ignore
import sys
from pathlib import Path

# Add the project root directory to the Python path.
# This ensures that 'app' and 'scraper' can be imported as top-level packages.
ROOT_DIR = Path(__file__).resolve().parent
sys.path.append(str(ROOT_DIR))


# For production, use RabbitMQ or Redis on a dedicated server
# celery_app = Celery("worker", broker="amqp://guest@localhost//")
celery_app = Celery("worker", broker="redis://localhost:6379/0", backend="redis://localhost:6379/0")

celery_app.conf.update(
    task_track_started=True,
)

# This imports the tasks so the worker can find them.
celery_app.autodiscover_tasks(['scraper'])