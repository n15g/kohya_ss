import time

import gradio as gr
from easygui import msgbox

from library.custom_logging import setup_logging
from .class_dataset import Dataset
from .class_dataset_editor_images_widget import DatasetEditorImagesWidget
from .class_dataset_editor_tags_widget import DatasetEditorTagsWidget
from .common_gui import get_folder_path

# Set up logging
log = setup_logging()

dataset = Dataset()


# Gradio UI
def gradio_dataset_editor_gui_tab(headless=False):
    with gr.Tab('Dataset Editor'):
        dataset_timestamp = gr.Text(visible=False)

        gr.Markdown(
            'This utility provides image and caption analysis for datasets as well as bulk tag manipulation tools.'
        )

        # File management
        with gr.Row():
            dataset_dir = gr.Textbox(
                label='Dataset directory',
                placeholder='Directory containing the images to caption',
                interactive=True,
            )
            folder_button = gr.Button(
                '📂', elem_id='open_folder_small', visible=(not headless)
            )

            load_button = gr.Button('Load/Refresh 🔃', elem_classes='load_button')
            caption_ext = gr.Textbox(
                label='Caption file extension',
                placeholder='Extension for caption file. eg: .txt, .caption',
                value='.txt',
                interactive=True,
            )
            save_button = gr.Button('Save 💾', elem_classes='save_button')

        # Results
        with gr.Row():
            with gr.Tab('Images'):
                DatasetEditorImagesWidget(dataset, dataset_timestamp)

            with gr.Tab('Tags'):
                DatasetEditorTagsWidget(dataset, dataset_timestamp)

    folder_button.click(
        get_folder_path,
        outputs=dataset_dir,
        show_progress=False,
    )

    load_button.click(
        load,
        [dataset_dir, caption_ext],
        dataset_timestamp
    )


def load(dataset_dir, caption_ext) -> str:
    dataset.clear()

    try:
        dataset.load(dataset_dir, caption_ext)
    except Exception as e:
        msgbox(e.args[0])

    return str(time.time())
