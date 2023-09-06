import os

IMAGE_EXTENSIONS = ('.png', '.jpg', '.jpeg', '.webp', '.bmp')


class DatasetEntry:
    """
    Entry in the dataset. Includes the training image and any caption data/tags located
    alongside.
    """
    filename: str
    image_dir: str
    image_path: str
    caption_path: str
    original_tags: list[str]
    tags: list[str]

    def __init__(self, ) -> None:
        super().__init__()
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

        if os.path.exists(self.caption_path):
            with open(self.caption_path, 'r', encoding='utf8') as f:
                caption = f.read()
                for tag in caption.split(','):
                    tag = tag.strip().lower()
                    self.original_tags.append(tag)
                    self.tags.append(tag)


class Dataset:
    """
    Representation of a training dataset containing images paired with captions/tags.
    """
    dataset_dir: str | None
    caption_ext: str | None
    entries: dict[str, DatasetEntry]
    size: int = 0

    def __init__(self) -> None:
        super().__init__()
        self.clear()

    def load(self, dataset_dir: str, caption_ext: str) -> None:
        if not dataset_dir or not os.path.exists(dataset_dir):
            raise ValueError('Dataset directory does not exist.')
        self.dataset_dir = dataset_dir

        if not caption_ext:
            raise ValueError('Please provide an extension for the caption files.')
        self.caption_ext = caption_ext

        for file in os.listdir(dataset_dir):
            if file.lower().endswith(IMAGE_EXTENSIONS):
                self._load_entry(os.path.join(dataset_dir, file))

    def clear(self) -> None:
        self.dataset_dir = None
        self.caption_ext = None
        self.entries = dict()
        self.size = 0

    def _load_entry(self, image_path: str) -> None:
        entry = DatasetEntry()
        entry.load(image_path, self.caption_ext)
        self.entries[image_path] = entry
        self.size += 1
