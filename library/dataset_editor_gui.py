import time

import gradio as gr
from easygui import msgbox

from library.custom_logging import setup_logging
from .class_dataset import Dataset
from .class_dataset_editor_duplicates_widget import DatasetEditorDuplicatesWidget
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
                interactive=True,
            )
            folder_button = gr.Button(
                '📂', elem_id='open_folder_small', visible=(not headless)
            )

            load_button = gr.Button('Load/Refresh 🔃')
            caption_ext = gr.Textbox(
                label='Caption file extension',
                value='.txt',
                interactive=True,
            )
            save_button = gr.Button('Save 💾')

        # Results
        with gr.Row(visible=False) as results_row:
            with gr.Tab('Tags'):
                DatasetEditorTagsWidget(dataset, dataset_timestamp)

            with gr.Tab('Duplicates'):
                DatasetEditorDuplicatesWidget(dataset, dataset_timestamp)

            with gr.Tab('Images'):
                DatasetEditorImagesWidget(dataset, dataset_timestamp)

    folder_button.click(
        get_folder_path,
        outputs=dataset_dir,
        show_progress=False,
    )

    load_button.click(
        fn=load,
        inputs=[dataset_dir, caption_ext],
        outputs=[dataset_timestamp, results_row]
    )

    save_button.click(
        fn=save
    )


def load(dataset_dir, caption_ext):
    dataset.clear()

    try:
        dataset.load(dataset_dir, caption_ext)
    except Exception as e:
        msgbox(e.args[0])

    return [
        str(time.time()),
        gr.Row.update(visible=True)
    ]


def save():
    dataset.save()
