import time

import gradio as gr

from library.class_dataset import Dataset


class TagDuplicate:
    entry: str
    tag: str
    count: int

    def __init__(self, entry: str, tag: str, count: int) -> None:
        super().__init__()
        self.entry = entry
        self.tag = tag
        self.count = count


class DatasetEditorDuplicatesWidget:
    dataset: Dataset
    dataset_timestamp: gr.Text
    selected_tag: gr.Text

    tag_duplicates_list: gr.Markdown()
    tag_duplicates_remove_button: gr.Button()

    def __init__(
            self,
            dataset: Dataset,
            dataset_timestamp: gr.Text
    ) -> None:
        self.dataset = dataset
        self.dataset_timestamp = dataset_timestamp

        with gr.Row():
            with gr.Column():
                self.tag_duplicates_remove_button = gr.Button('Remove duplicates')
                self.tag_duplicates_list = gr.Markdown(
                    label='Duplicate Tags',
                    elem_classes='de_panel'
                )

        dataset_timestamp.change(
            fn=self._on_dataset_change,
            outputs=[
                self.tag_duplicates_list,
                self.tag_duplicates_remove_button
            ]
        )
        self.tag_duplicates_remove_button.click(
            fn=self._on_tag_duplicates_remove_button_click,
            outputs=self.dataset_timestamp
        )

    def _on_dataset_change(self):
        tag_duplicates = self._get_tag_duplicates()

        markdown = ""
        if len(tag_duplicates) > 0:
            for dupe in tag_duplicates:
                markdown += f"* {dupe.entry}:{dupe.tag} ({dupe.count})\n"
        else:
            markdown = "No tag duplicates found"

        return [
            gr.Markdown.update(value=markdown),
            gr.Button.update(visible=len(tag_duplicates) > 0)
        ]

    def _on_tag_duplicates_remove_button_click(self):
        self.dataset.remove_duplicate_tags()
        return str(time.time())

    def _get_tag_duplicates(self) -> list[TagDuplicate]:
        duplicates: list[TagDuplicate] = list()

        for entry in self.dataset.entries.values():
            seen = set()
            counts = dict[str, int]()

            for tag in entry.tags:
                if tag in seen:
                    counts[tag] = counts.get(tag, 1) + 1
                else:
                    seen.add(tag)

            for tag, count in counts.items():
                duplicates.append(TagDuplicate(entry.key, tag, count))

        return duplicates
