import time

import gradio as gr

from library.class_dataset import Dataset


class DatasetEditorTagsWidget:
    dataset: Dataset
    dataset_timestamp: gr.Text

    selected_tag: gr.Text
    tag_distribution_graph: gr.Label

    def __init__(
            self,
            dataset: Dataset,
            dataset_timestamp: gr.Text
    ) -> None:
        self.dataset = dataset
        self.dataset_timestamp = dataset_timestamp

        with gr.Row():
            self.selected_tag = gr.Text(visible=False)
            self.tag_distribution_graph = gr.Label(
                label='Tag Distribution',
                scale=2,
                elem_classes=["de_panel", "de_tags_distribution"]
            )

            self.selected_tag_widget = DatasetEditorSelectedTagWidget(
                self.dataset,
                self.dataset_timestamp,
                self.selected_tag
            )

        self.dataset_timestamp.change(fn=self._update_tag_distribution, outputs=self.tag_distribution_graph)
        self.tag_distribution_graph.select(fn=self._on_select_tag, outputs=self.selected_tag)

    def _update_tag_distribution(self) -> dict[str, float]:
        counts: dict[str, int] = dict()
        percents: dict[str, float] = dict()

        for entry in self.dataset.entries.values():
            for tag in entry.tags:
                counts[tag] = counts.get(tag, 0) + 1

        for k, v in counts.items():
            percents[k] = v / self.dataset.size

        return gr.Label.update(value=percents)

    def _on_select_tag(self, event: gr.SelectData) -> gr.Text.update:
        return gr.Text.update(value=event.value)


class DatasetEditorSelectedTagWidget:
    dataset: Dataset
    dataset_timestamp: gr.Text
    selected_tag: gr.Text

    heading_label: gr.Markdown
    delete_tag_button: gr.Button
    rename_tag_text: gr.Text
    rename_tag_button: gr.Button
    entry_list: gr.HighlightedText

    def __init__(
            self,
            dataset: Dataset,
            dataset_timestamp: gr.Text,
            selected_tag: gr.Text
    ) -> None:
        super().__init__()
        self.dataset = dataset
        self.dataset_timestamp = dataset_timestamp
        self.selected_tag = selected_tag

        with gr.Column():
            with gr.Row():
                self.heading_label = gr.Markdown()
                self.delete_tag_button = gr.Button('Delete 💣', scale=0)
            with gr.Row():
                self.rename_tag_text = gr.Text(label='Rename Tag')
                self.rename_tag_button = gr.Button('Rename ✏️', scale=0, elem_classes="small_button")
            with gr.Row():
                self.entry_list = gr.HighlightedText(
                    label='Entries',
                    elem_classes=["de_panel", "de_file_list"]
                )

        self.dataset_timestamp.change(
            fn=self._on_dataset_change,
            inputs=selected_tag,
            outputs=selected_tag
        )

        self.selected_tag.change(
            fn=self._on_selected_tag_change,
            inputs=selected_tag,
            outputs=[
                self.heading_label,
                self.delete_tag_button,
                self.rename_tag_text,
                self.rename_tag_button,
                self.entry_list
            ]
        )

        self.delete_tag_button.click(
            fn=self._on_delete_tag,
            inputs=self.selected_tag,
            outputs=[self.selected_tag, self.dataset_timestamp]
        )

        self.rename_tag_button.click(
            fn=self._on_rename_tag,
            inputs=[
                self.selected_tag,
                self.rename_tag_text
            ],
            outputs=[
                self.selected_tag,
                self.dataset_timestamp
            ]
        )

    def _on_dataset_change(self, selected_tag: str):
        if selected_tag not in self.dataset.tags:
            return None
        return selected_tag

    def _on_selected_tag_change(self, selected_tag: str):
        interactive = selected_tag is not None
        title = f"# {selected_tag}" if selected_tag is not None else "# Select a tag"

        samples = []
        if selected_tag is not None:
            entries = self.dataset.get_entries_with_tag(selected_tag)
            samples = list(map(
                lambda x: (x.filename, x.instance_path if len(x.instance_path) > 1 else None),
                entries
            ))

        return [
            gr.Markdown.update(value=title),  # heading_label
            gr.Button.update(interactive=interactive),  # delete_button
            gr.Text.update(value=selected_tag, interactive=interactive),  # rename_text
            gr.Button.update(interactive=interactive),  # rename_button
            gr.HighlightedText.update(value=samples),  # entry_list
        ]

    def _on_delete_tag(self, tag: str):
        self.dataset.delete_tag(tag)
        return [
            None,  # selected_tag
            str(time.time())  # dataset_timestamp,
        ]

    def _on_rename_tag(self, old: str, new: str):
        self.dataset.rename_tag(old, new)
        return [
            new,  # selected_tag
            str(time.time()),  # dataset_timestamp
        ]
