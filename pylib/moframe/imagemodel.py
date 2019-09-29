from PyQt5.QtGui import QImage
import threading
import os
import os.path
from collections import defaultdict, deque
import random
import time
import gc


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
        self.cache = deque()
        self.active = True
        self.idx = -1

    def run(self):
        """
        Start listing and pre-loading images. Then continue to pre-load images as needed.
        """
        for (root, dirs, files) in os.walk(self.basepath):
            for file in files:
                # jpeg files in dirs whose name do not start with underscore
                if not os.path.split(root)[-1].startswith("_"):
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
                if candidates:
                    root, file = random.choice(tuple(candidates))
                    img = self.loadImage(root, file)
                    if img.isNull():
                        self.categories[""].remove((root, file))
                    else:
                        self.loaded[(root, file)] = img

    def loadImage(self, root, file):
        """
        Load image from disk.

        Args:
            root: Full path of directory.
            file: Filename.

        Returns:
            QImage: image.
        """
        img = QImage(os.path.join(root, file))
        return img

    def nextImage(self):
        """
        Designate next image, put it on the history-queue and return it.

        Returns:
            (str, str, QImage): (root, filename, image)
        """
        self.idx = max(-1, self.idx - 1)
        if self.idx == -1:
            self.addImage()
        item = self.getCurrentImage()
        return item

    def prevImage(self):
        """
        Designate next image, put it on the history-queue and return it.

        Returns:
            (str, str, QImage): (root, filename, image)
        """
        self.idx = min(len(self.history) - 1, self.idx + 1)
        item = self.getCurrentImage()
        return item

    def hasPrevImage(self):
        """
        Returns:
            True if current image is not the first one in the history list.
        """
        return self.idx < len(self.history) - 1

    def hasNextImage(self):
        """
        Returns:
            True if current image is not the last one in the history list.
        """
        return self.idx >= 0

    def getCurrentImage(self):
        """
        Return current image.

        Returns:
            (str, str, QImage): (root, filename, image)
        """
        if self.idx == -1:
            item = self.cache[-1]
        elif self.idx >= 0:
            key = self.history[-1 - self.idx]
            for kk, ii in self.cache:
                if key == kk:
                    item = (kk, ii)
                    break
            else:
                item = (key, self.loadImage(*key))
        return item[0] + (item[1],)

    def addImage(self):
        """
        Select a new image from the preloaded cache and move it to the front of
        the history.
        """
        for _ in range(100):
            if len(self.loaded) == 0:
                time.sleep(0.1)
        if len(self.loaded) == 0:
            raise RuntimeError("No image available.")
        with self.lock:
            item = self.loaded.popitem()
            self.cache.append(item)
            self.history.append(item[0])
            while len(self.history) > 10000:
                self.history.popleft()
            while len(self.cache) > 10:
                self.cache.popleft()
