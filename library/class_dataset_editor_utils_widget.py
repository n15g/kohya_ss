import os
import time

import gradio as gr

from library.class_dataset import Dataset


class DatasetEditorUtilsWidget:
    dataset: Dataset
    dataset_timestamp: gr.Text
    selected_tag: gr.Text

    gather_small_button: gr.Button
    rename_to_md5_button: gr.Button

    def __init__(
            self,
            dataset: Dataset,
            dataset_timestamp: gr.Text
    ) -> None:
        self.dataset = dataset
        self.dataset_timestamp = dataset_timestamp

        with gr.Row():
            self.gather_small_button = gr.Button(value="Gather small images")
            self.rename_to_md5_button = gr.Button(value="Rename to MD5")

        self.gather_small_button.click(fn=self._gather_small)
        self.rename_to_md5_button.click(fn=self._rename_to_md5, outputs=self.dataset_timestamp)

    def _gather_small(self) -> None:
        for image in self.dataset.entries.values():
            x2 = (1024 * 1024)
            x4 = (1024 * 1024) / 2
            if image.area < x4:
                x4_path = os.path.join(image.image_dir, "x4")
                os.makedirs(x4_path, exist_ok=True)
                os.rename(image.image_path, os.path.join(x4_path, f"{image.filename}{image.extension}"))
                if os.path.exists(image.caption_path):
                    os.rename(image.caption_path, os.path.join(x4_path, f"{image.filename}{self.dataset.caption_ext}"))
                continue

            if image.area < x2:
                x2_path = os.path.join(image.image_dir, "x2")
                os.makedirs(x2_path, exist_ok=True)
                os.rename(image.image_path, os.path.join(x2_path, f"{image.filename}{image.extension}"))
                if os.path.exists(image.caption_path):
                    os.rename(image.caption_path, os.path.join(x2_path, f"{image.filename}{self.dataset.caption_ext}"))
                continue

    def _rename_to_md5(self) -> str:
        for image in self.dataset.entries.values():
            os.rename(image.image_path, os.path.join(image.image_dir, f"{image.hash}{image.extension}"))
            if os.path.exists(image.caption_path):
                os.rename(image.caption_path, os.path.join(image.image_dir, f"{image.hash}{self.dataset.caption_ext}"))
        self.dataset.reload()

        return str(time.time())
