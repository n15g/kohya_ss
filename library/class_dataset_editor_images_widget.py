import gradio as gr

from library.class_dataset import Dataset


class DatasetEditorImagesWidget:
    dataset: Dataset
    dataset_timestamp: gr.Text
    selected_tag: gr.Text

    area_distribution_graph: gr.Label
    dimension_distribution_graph: gr.Label
    aspect_ratio_distribution_graph: gr.Label
    tag_distribution_graph: gr.Label

    def __init__(
            self,
            dataset: Dataset,
            dataset_timestamp: gr.Text
    ) -> None:
        self.dataset = dataset
        self.dataset_timestamp = dataset_timestamp

        with gr.Row():
            self.area_distribution_graph = gr.Label(
                label='Area Distribution',
                elem_classes='de_panel'
            )

            self.dimension_distribution_graph = gr.Label(
                label='Dimensions Distribution',
                elem_classes='de_panel'
            )
            self.aspect_ratio_distribution_graph = gr.Label(
                label='Aspect Ratio Distribution',
                elem_classes='de_panel'
            )

        dataset_timestamp.change(
            self._on_dataset_change,
            outputs=[
                self.area_distribution_graph,
                self.dimension_distribution_graph,
                self.aspect_ratio_distribution_graph
            ]
        )

    def _on_dataset_change(self):
        return [
            self._update_size_distribution(),
            self._update_dimension_distribution(),
            self._update_aspect_ratio_distribution()
        ]

    def _update_size_distribution(self) -> dict:
        counts: dict[str, int] = dict()
        percents: dict[str, float] = dict()

        for entry in self.dataset.entries.values():
            area = f"{entry.area / 1_000_000:0.1f}M"
            counts[area] = counts.get(area, 0) + 1

        for k, v in counts.items():
            percents[k] = v / self.dataset.size

        return gr.Label.update(value=percents)

    def _update_dimension_distribution(self) -> dict:
        counts: dict[str, int] = dict()
        percents: dict[str, float] = dict()

        for entry in self.dataset.entries.values():
            dims = f"{entry.width}x{entry.height}"
            counts[dims] = counts.get(dims, 0) + 1

        for k, v in counts.items():
            percents[k] = v / self.dataset.size

        return gr.Label.update(value=percents)

    def _update_aspect_ratio_distribution(self) -> dict:
        counts: dict[str, int] = dict()
        percents: dict[str, float] = dict()

        for entry in self.dataset.entries.values():
            counts[entry.aspect_ratio] = counts.get(entry.aspect_ratio, 0) + 1

        for k, v in counts.items():
            percents[k] = v / self.dataset.size

        return gr.Label.update(value=percents)
