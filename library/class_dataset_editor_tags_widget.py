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
            self.tag_distribution_graph = gr.Label(label='Tag Distribution')

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

    block: gr.Column
    heading_label: gr.Markdown
    delete_tag_button: gr.Button

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

        with gr.Column(visible=False) as self.block:
            self.heading_label = gr.Markdown()
            self.delete_tag_button = gr.Button('Delete Tag 💣')

        self.dataset_timestamp.change(
            fn=self._on_dataset_change,
            inputs=selected_tag,
            outputs=selected_tag
        )

        self.selected_tag.change(
            fn=self._on_selected_tag_change,
            inputs=selected_tag,
            outputs=[self.block, self.heading_label]
        )

        self.delete_tag_button.click(
            self._on_delete_tag,
            self.selected_tag
        )

    def _on_dataset_change(self, selected_tag: str) -> gr.Text.update:
        if selected_tag is None or selected_tag not in self.dataset.tags:
            return None
        return selected_tag

    def _on_selected_tag_change(self, selected_tag: str) -> [gr.Blocks.update, gr.Markdown.update]:
        return [
            gr.Column.update(visible=selected_tag is not None),
            gr.Markdown.update(value=f"# Edit tag [{selected_tag}]")
        ]

    def _on_delete_tag(self, tag):
        self.dataset.delete_tag(tag)
