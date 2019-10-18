import threading
import os
import os.path
from collections import defaultdict, deque
import random
import time

from PyQt5.QtGui import QImage, QMovie
from PyQt5.QtCore import Qt, QSize


EXT_IMAGE = ("jpg", "bmp", "png")
EXT_ANIMATION = ("gif", "mov")
EXT_ALL = EXT_IMAGE + EXT_ANIMATION


class GalleryObject(object):
    qdata = None
    qpreview = None
    contents = "unknown"
    path = ("", "")
    fullsize = (1280, 800)
    previewsize = (200, 200)
    error = None
    validated = False

    def __init__(self, path, **kwargs):
        root, file = path
        self.path = path
        ext = file.rsplit(".", 1)[-1].lower()
        if ext in EXT_IMAGE:
            self.contents = "image"
        elif ext in EXT_ANIMATION:
            self.contents = "animation"
        for k, v in kwargs.items():
            setattr(self, k, v)

    @classmethod
    def fit(cls, img, size):
        """
        Fit image in size by scaling proportionally to cover (touch from outside),
        centering the image, and cropping it to the exact size.

        Args:
            img: A QImage object.
            size: Desired pixel width and height tuple.

        Returns: New QImage of exact given size.
        """
        width, height = size
        img = img.scaled(width, height, aspectRatioMode=Qt.KeepAspectRatioByExpanding)
        imw, imh = img.width(), img.height()
        ix = max(0, (imw - width) / 2)
        iy = max(0, (imh - height) / 2)
        img = img.copy(ix, iy, width, height)
        return img

    def getQImage(self):
        """
        Returns: QImage object containing the still image data.
        """
        if not self.contents == "image":
            return None
        if self.qdata is None and not self.error:
            root, file = self.path
            img = QImage(os.path.join(root, file))
            if img.isNull():
                self.error = "failed to load"
                return None
            self.qdata = self.fit(img, self.fullsize)
        return self.qdata

    def getQMovie(self):
        """
        Returns: Qmovie object containing the animation.
        """
        if not self.contents == "animation":
            return None
        if self.qdata is None and not self.error:
            root, file = self.path
            img = QMovie(os.path.join(root, file))
            if not img.isValid():
                self.error = "failed to load: " + img.lastError()
                return None
            img.setScaledSize(QSize(*self.fullsize))
            self.qdata = img
        return self.qdata

    def getQPreview(self):
        """
        Returns: QImage object containing a sized image data.
        """
        if self.qpreview is None:
            if self.contents == "image":
                img = self.getQImage()
                if img is not None:
                    self.qpreview = self.fit(img, self.previewsize)
            if self.contents == "animation":
                self.qpreview = "PLACEHOLDER-FIXME!"
        return self.qpreview

    def load(self):
        """
        (Pre)load the image object into memory.
        """
        self.getQPreview()

    def unload(self):
        """
        Free memory by releasing cached image.
        """
        self.qdata = None

    def forget(self):
        """
        Free memory by releasing all image data, including preview.
        """
        self.unload()
        self.qpreview = None

    def valid(self):
        """
        Try to load object and return True iff successful.

        Returns: True if the image can be loaded correctly.
        """
        if self.contents == "image":
            return self.getQImage() is not None
        if self.contents == "animation":
            return self.getQMovie() is not None


class GalleryModel(threading.Thread):
    def __init__(self, cfg):
        basepath = cfg.get("photos-basepath", ".")
        threading.Thread.__init__(self)
        self.cfg= cfg
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
                # files with known extensions in dirs whose name do not start with underscore
                if not os.path.split(root)[-1].startswith("_"):
                    ext = file.rsplit(".", 1)[-1].lower()
                    if ext in EXT_ALL:
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
                    if not img.valid():
                        print("Error: bad image file:", img.contents, img.error)
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
        obj = GalleryObject((root, file))
        if "target-size" in self.cfg:
            obj.fullsize = self.cfg["target-size"]
        obj.load()
        return obj

    def nextImage(self):
        """
        Designate next image, put it on the history-queue and return it.

        Returns:
            (str, str, QImage): (root, filename, image)
        """
        self.idx = max(0, self.idx - 1)
        if self.idx <= 0:
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
        if len(self.history) == 0:
            print("Error: no images to display")
            return None, None, None
        elif len(self.history) <= self.idx:
            print("Error: invalid image index")
            return None, None, None
        else:
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
        if len(self.loaded) == 0:
            print("No new image available.")
            return
        with self.lock:
            item = self.loaded.popitem()
            self.cache.append(item)
            self.history.append(item[0])
            while len(self.history) > 10000:
                self.history.popleft()
            while len(self.cache) > 10:
                self.cache.popleft()



