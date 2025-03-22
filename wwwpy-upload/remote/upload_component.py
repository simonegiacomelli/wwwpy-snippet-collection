import asyncio
import base64
import logging
from dataclasses import dataclass
from typing import Callable

import js
import wwwpy.remote.component as wpc
from pyodide.ffi import create_proxy, JsException
from wwwpy.remote import dict_to_js

logger = logging.getLogger(__name__)


class UploadComponent(wpc.Component, tag_name='wwwpy-quickstart-upload'):
    file_input: js.HTMLInputElement = wpc.element()
    uploads: js.HTMLElement = wpc.element()
    dropzone: js.HTMLElement = wpc.element()  # New element for drop zone

    @property
    def multiple(self) -> bool:
        return self.file_input.hasAttribute('multiple')

    @multiple.setter
    def multiple(self, value: bool):
        self.file_input.toggleAttribute('multiple', value)

    def init_component(self):
        self.element.attachShadow(dict_to_js({'mode': 'open'}))
        # language=html
        self.element.shadowRoot.innerHTML = """
<div data-name="dropzone" style="border: 2px dashed #ccc; padding: 20px; text-align: center; margin-bottom: 10px; cursor: pointer;">
    <p>Drag and drop files here or</p>
    <input data-name="file_input" placeholder="input1" type="file" multiple style="display: inline-block;">
</div>
<div data-name="uploads"></div>
        """

    def dropzone__dragover(self, event):
        # Prevent default to allow drop
        event.preventDefault()
        event.stopPropagation()
        # Add visual feedback
        self.dropzone.style.borderColor = '#0099ff'
        self.dropzone.style.backgroundColor = 'rgba(0, 153, 255, 0.1)'

    def dropzone__dragleave(self, event):
        event.preventDefault()
        event.stopPropagation()
        # Reset visual feedback
        self.dropzone.style.borderColor = '#ccc'
        self.dropzone.style.backgroundColor = 'transparent'

    def dropzone__drop(self, event):
        event.preventDefault()
        event.stopPropagation()
        # Reset visual feedback
        self.dropzone.style.borderColor = '#ccc'
        self.dropzone.style.backgroundColor = 'transparent'

        # Get files from the drop event
        files = event.dataTransfer.files
        self._process_files(files)

    def dropzone__click(self, event):
        # If they click the drop zone but not on the input, trigger the file input
        if event.target != self.file_input:
            self.file_input.click()

    def _process_files(self, files):
        # Process the files just like in the change event
        for file in files:
            progress = UploadProgressComponent()
            self.uploads.appendChild(progress.element)
            asyncio.create_task(progress.upload(file))

    async def file_input__change(self, event):
        files = self.file_input.files
        self._process_files(files)
        self.file_input.value = ''


@dataclass
class UploadProgress:
    file: js.File
    bytes_uploaded: int
    total_bytes: int
    abort: bool = False  # Flag that can be set to stop the upload
    failure: Exception | None = None

    @property
    def percentage(self) -> float:
        """Calculate the upload percentage."""
        if self.total_bytes == 0:
            return 0.0
        if self.completed:
            return 100.0
        return round((self.bytes_uploaded / self.total_bytes) * 100, 2)

    @property
    def completed(self) -> bool:
        """Check if the upload is complete."""
        return self.bytes_uploaded >= self.total_bytes

    @property
    def still_uploading(self) -> bool:
        return not self.abort and not self.completed and self.failure is None


async def _read_chunk(blob: js.Blob) -> js.ArrayBuffer:
    """
    Read a chunk of a file as an ArrayBuffer.

    Args:
        blob: JavaScript Blob object to read

    Returns:
        ArrayBuffer containing the blob data
    """
    future: asyncio.Future = asyncio.Future()

    def onload(event):
        future.set_result(reader.result)

    def onerror(event):
        future.set_exception(Exception(f"Error reading file: {reader.error}"))

    reader: js.FileReader = js.FileReader.new()
    reader.onload = create_proxy(onload)
    reader.onerror = create_proxy(onerror)
    reader.readAsArrayBuffer(blob)

    return await future


async def upload_file(file: js.File,
                      progress_callback: Callable[[UploadProgress], None] = None,
                      chunk_size: int = pow(2, 18)) -> None:
    """
    Upload a file in chunks to the server.

    Args:
        file: JavaScript File object to upload
        progress_callback: Optional callback function that receives an UploadProgress object
                          to report progress to the UI
        chunk_size: Size of chunks to upload (default: 2^18 bytes)

    Returns:
        None
    """
    logger.info(f'upload file: {file.name} {file.size} {file.type}')
    if not progress_callback:
        progress_callback = lambda _: None

    total_size = file.size
    progress = UploadProgress(file=file, bytes_uploaded=0, total_bytes=total_size)
    try:
        from server import rpc
        await rpc.upload_init(file.name, file.size)

        offset = 0

        progress_callback(progress)

        while offset < total_size and not progress.abort:
            chunk: js.Blob = file.slice(offset, offset + chunk_size)
            array_buffer = await _read_chunk(chunk)

            logger.info(f'offset={offset}')
            b64str = base64.b64encode(array_buffer.to_py()).decode()
            await rpc.upload_append(file.name, b64str)

            # Update progress
            chunk_size_actual = min(chunk_size, total_size - offset)
            offset += chunk_size_actual
            progress.bytes_uploaded = offset

            # Report progress
            progress_callback(progress)

        # Final progress report
        if progress.completed:
            progress_callback(progress)

        logger.info(f'Upload completed: {file.name}')

    except Exception as e:
        logger.exception(e)
        progress.failure = e
        progress_callback(progress)



class UploadProgressComponent(wpc.Component):
    file_input: js.HTMLInputElement = wpc.element()
    progress: js.HTMLProgressElement = wpc.element()
    progress_label: js.HTMLLabelElement = wpc.element()
    label: js.HTMLInputElement = wpc.element()

    def init_component(self):
        # language=html
        self.element.innerHTML = """
<div data-name="progress_label" style='padding: 0.5em'>
    <progress data-name="progress"></progress>
    &nbsp;<span data-name="label"></span>
</div>"""

    async def upload(self, file: js.File, chunk_size: int = pow(2, 18)):
        """Upload a file and update the UI with progress."""
        await upload_file(file, self._update_progress, chunk_size)


    def _update_progress(self, progress: UploadProgress):
        """Callback function to update the UI with upload progress."""
        self.progress.max = progress.total_bytes
        self.progress.value = progress.bytes_uploaded

        # Update label
        label = f'{progress.file.name}: '
        if progress.completed:
            label += 'upload completed'
            self._fade_out()
        elif progress.failure:
            label += f'error: {progress.failure}'
        else:
            label += f'{progress.percentage}%'

        self.label.textContent = label

    def _fade_out(self, fade_delay_secs=3):
        """Fade out and remove the progress element after completion."""
        self.element.style.opacity = '1'
        self.element.style.transition = f'opacity {fade_delay_secs}s'
        self.element.style.opacity = '0'

        async def _remove():
            await asyncio.sleep(fade_delay_secs)
            self.element.remove()

        asyncio.create_task(_remove())
