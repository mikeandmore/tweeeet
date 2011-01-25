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
            self.notification_cb = lambda status, text: sys.stdout.write('[info]: %s\n' % text)

        def run(self):
            last_error = None
            while True:
                if self.queue.qsize() == 0:
                    if last_error is None:
                        self.notification_cb(0, 'done')
                    else:
                        self.notification_cb(-1, last_error)
                        last_error = None
                handler, text = self.queue.get(block=True, timeout=None)
                try:
                    if text is not None:
                        self.notification_cb(1, text)
                    handler()
                except Exception, e:
                    last_error = str(e)
                    traceback.print_exc(file=sys.stderr)
                self.queue.task_done()

    __new__ = singleton_new

    def __init__(self):
        self.queue = Queue.Queue()
        self.worker = Pipeline.PipelineWorker(self.queue)
        self.worker.daemon = True
        self.worker.start()

    def add_handler(self, handler, text=None):
        self.queue.put((handler, text), block=True, timeout=None)

    def set_notification_callback(self, cb):
        self.worker.notification_cb = cb
