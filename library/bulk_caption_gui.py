import gradio as gr
from easygui import msgbox

from library.custom_logging import setup_logging
from .class_dataset import Dataset
from .common_gui import get_folder_path

# Set up logging
log = setup_logging()

dataset = Dataset()


def load(dataset_dir, caption_ext) -> dict[str, float]:
    dataset.clear()

    try:
        dataset.load(dataset_dir, caption_ext)
    except Exception as e:
        msgbox(e.args[0])
        return gr.Text.update()

    tag_counts: dict[str, int] = dict()
    tag_percents: dict[str, float] = dict()

    for entry in dataset.entries.values():
        for tag in entry.tags:
            tag_counts[tag] = tag_counts.get(tag, 0) + 1

    for k, v in tag_counts.items():
        tag_percents[k] = v / dataset.size

    return tag_percents


# Gradio UI
def gradio_bulk_caption_gui_tab(headless=False):
    with gr.Tab('Bulk Captioning'):
        gr.Markdown(
            'This utility allows bulk manipulation of image tags.'
        )

        with gr.Row():
            dataset_dir = gr.Textbox(
                label='Image folder to caption',
                placeholder='Directory containing the images to caption',
                interactive=True,
            )
            folder_button = gr.Button(
                '📂', elem_id='open_folder_small', visible=(not headless)
            )

            load_button = gr.Button('Load 🔃', elem_id='load_button')
            caption_ext = gr.Textbox(
                label='Caption file extension',
                placeholder='Extension for caption file. eg: .caption, .txt',
                value='.txt',
                interactive=True,
            )
            save_button = gr.Button(label='Save 💾', elem_id='save_button')

        # Caption Section
        with gr.Row():
            histogram = gr.Label(label='Histogram')

        folder_button.click(
            get_folder_path,
            outputs=dataset_dir,
            show_progress=False,
        )

        load_button.click(
            load,
            [dataset_dir, caption_ext],
            histogram
        )
