from threading import Thread
from utils import singleton_new
import Queue
import traceback
import sys

class Pipeline(object):
    class PipelineWorker(Thread):
        def __init__(self, queue):
            Thread.__init__(self)
            self.queue = queue

        def run(self):
            while True:
                handler = self.queue.get(block=True, timeout=None)
                try:
                    handler()
                except:
                    traceback.print_exc(file=sys.stderr)
                self.queue.task_done()

    __new__ = singleton_new

    def __init__(self):
        self.queue = Queue.Queue()
        self.worker = Pipeline.PipelineWorker(self.queue)
        self.worker.daemon = True
        self.worker.start()

    def add_handler(self, handler):
        self.queue.put(handler, block=True, timeout=None)
    
