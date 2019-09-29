from PyQt5.QtGui import QImage
import threading
import os
from collections import defaultdict, deque
import random
import time


class ImageModel(threading.Thread):
    def __init__(self, basepath):
        threading.Thread.__init__(self)
        self.daemon = True
        self.basepath = basepath
        self.categories = defaultdict(set)
        self.count = 0
        self.loaded = {}
        self.lock = threading.Lock()
        self.history = deque()
        self.active = True

    def run(self):
        """
        Start listing and pre-loading images.
        Continue to pre-load images as needed.
        """
        for (root, dirs, files) in os.walk(self.basepath):
            for file in files:
                if file.lower().endswith(".jpg"):
                    self.categories[""].add((root, file))
                    self.count += 1
                    if self.count % 10 == 0:
                        self.preloadStep()
                    if not self.active:
                        return
        while self.active:
            self.preloadStep()
            time.sleep(0.1)

    def preloadStep(self):
        """
        Preload one image from the collection.
        """
        if len(self.loaded) < 10:
            with self.lock:
                candidates = self.categories[""] - set(self.loaded)
                root, file = random.choice(tuple(candidates))
                img = QImage(os.path.join(root, file))
                if img.isNull():
                    self.categories[""].remove((root, file))
                else:
                    self.loaded[(root, file)] = img
                    print("loaded:", (root, file))

    def nextImage(self):
        """
        Designate next image, put it on the history-queue and return it.

        Returns:
            (str, str, QImage): (root, filename, image)
        """
        for _ in range(100):
            if len(self.loaded) == 0:
                time.sleep(0.1)
        if len(self.loaded) == 0:
            raise RuntimeError("No image available.")
        with self.lock:
            item = self.loaded.popitem()
            self.history.append(item)
            while len(self.history) > 100:
                self.history.popleft()
        return item[0] + (item[1],)

