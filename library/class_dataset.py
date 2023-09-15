import concurrent.futures
import hashlib
import os

from PIL import Image

from library.utils import calculate_aspect_ratio

IMAGE_EXTENSIONS = ('.png', '.jpg', '.jpeg', '.webp', '.bmp')

executor = concurrent.futures.ProcessPoolExecutor(4)


class DatasetEntry:
    """
    Entry in the dataset. Includes the training image and any caption data/tags located
    alongside.
    """
    name: str
    filename: str
    hash: str
    width: int
    height: int
    aspect_ratio: str
    image_dir: str
    image_path: str
    caption_path: str
    original_tags: list[str]
    tags: list[str]

    def __init__(self, name: str) -> None:
        super().__init__()
        self.name = name
        self.original_tags = list()
        self.tags = list()

    def load(self, image_path: str, caption_ext: str) -> None:
        """
        Load image and caption data from a given image path.
        Captions are assumed to me located alongside the image in a file with the same base name
        and the given caption file extension.
        Args:
            image_path: Path to the image file.
            caption_ext: Extension for caption data.
        """
        self.image_dir = os.path.dirname(image_path)
        self.filename = os.path.splitext(os.path.basename(image_path))[0]
        self.image_path = image_path
        self.caption_path = os.path.join(self.image_dir, self.filename) + caption_ext

        if os.path.exists(self.image_path):
            with open(self.image_path, "rb") as f:
                self.hash = hashlib.sha256(f.read()).hexdigest()
            with Image.open(image_path) as img:
                self.width, self.height = img.size

            x, y = calculate_aspect_ratio(self.width, self.height)
            self.aspect_ratio = f"{x}:{y}"

        if os.path.exists(self.caption_path):
            with open(self.caption_path, 'r', encoding='utf8') as f:
                caption = f.read()
                for tag in caption.split(','):
                    tag = tag.strip().lower()
                    self.original_tags.append(tag)
                    self.tags.append(tag)

    def delete_tag(self, tag: str) -> None:
        """
        Delete the given tag from this entry's captions.
        Args:
            tag: The tag to delete
        """
        try:
            self.tags.remove(tag)
        except ValueError:
            # no-op. Tag doesn't exist, nothing to do
            pass

    def rename_tag(self, old, new):
        """
        Rename a tag in this entry's captions.
        Args:
            old: Old value
            new: New value
        """
        self.tags = list(map(lambda e: e.replace(old, new), self.tags))


class Dataset:
    """
    Representation of a training dataset containing images paired with captions/tags.
    """
    dataset_dir: str | None
    caption_ext: str | None
    entries: dict[str, DatasetEntry]
    tags: set[str]
    size: int = 0

    def __init__(self) -> None:
        super().__init__()
        self._on_change_listeners = set()
        self.clear()

    def load(self, dataset_dir: str, caption_ext: str) -> None:
        if not dataset_dir or not os.path.exists(dataset_dir):
            raise ValueError('Dataset directory does not exist.')
        self.dataset_dir = dataset_dir

        if not caption_ext:
            raise ValueError('Please provide an extension for the caption files.')
        self.caption_ext = caption_ext

        for root, dirs, files in os.walk(dataset_dir):
            for file in files:
                if file.lower().endswith(IMAGE_EXTENSIONS):
                    entry = self._load_entry(os.path.join(root, file))
                    self.entries[entry.name] = entry
        self.size = len(self.entries)
        self._update_tags()

    def clear(self) -> None:
        self.tags = set()
        self.dataset_dir = None
        self.caption_ext = None
        self.entries = dict()
        self.size = 0

    def _load_entry(self, image_path: str) -> DatasetEntry:
        name = os.path.relpath(image_path, self.dataset_dir)
        entry = DatasetEntry(name)
        entry.load(image_path, self.caption_ext)
        return entry

    def _update_tags(self):
        self.tags = set()
        for entry in self.entries.values():
            self.tags.update(entry.tags)

    def delete_tag(self, tag: str) -> None:
        """
        Remove a tag from the dataset, purging it from all entries in the set.
        Args:
            tag: The tag to remove
        """
        for entry in self.entries.values():
            entry.delete_tag(tag)
        self._update_tags()

    def rename_tag(self, old: str, new: str) -> None:
        """
        Rename a tag across the whole dataset.
        Args:
            old: Old value
            new: New value
        """
        for entry in self.entries.values():
            entry.rename_tag(old, new)
        self._update_tags()
