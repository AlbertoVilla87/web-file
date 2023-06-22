from haystack.utils import launch_es
import time
from modeling.haystack import DocumentStore, Reader
from processing.transcripts import Transcripts
from processing.translation import Translator

from preparation.data_manager import DataManager

launch_es()
time.sleep(20)