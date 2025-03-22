from __future__ import annotations
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
    dropzone: js.HTMLElement = wpc.element()
    upload_icon: js.HTMLElement = wpc.element()
    button: js.HTMLElement = wpc.element()

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
<style>
    @keyframes pulse {
        0% { transform: scale(1); }
        50% { transform: scale(1.05); }
        100% { transform: scale(1); }
    }
    
    @keyframes progress-animation {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    
    .dropzone {
        border: 2px dashed #ccc;
        border-radius: 8px;
        padding: 25px;
        text-align: center;
        margin-bottom: 15px;
        cursor: pointer;
        transition: all 0.3s ease;
        background-color: rgba(245, 245, 245, 0.6);
        box-shadow: 0 2px 6px rgba(0, 0, 0, 0.05);
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    
    .dropzone:hover {
        border-color: #0099ff;
        background-color: rgba(0, 153, 255, 0.05);
    }
    
    .upload-icon {
        width: 48px;
        height: 48px;
        margin: 0 auto 15px;
        fill: #666;
        transition: fill 0.3s ease;
    }
    
    .dropzone:hover .upload-icon {
        fill: #0099ff;
    }
    
    .file-button {
        background-color: #0099ff;
        color: white;
        border: none;
        border-radius: 20px;
        padding: 8px 16px;
        font-size: 14px;
        cursor: pointer;
        transition: all 0.2s ease;
        margin-top: 10px;
        font-weight: 500;
        box-shadow: 0 2px 4px rgba(0, 0, 153, 0.2);
    }
    
    .file-button:hover {
        background-color: #007acc;
        transform: translateY(-2px);
        box-shadow: 0 4px 6px rgba(0, 0, 153, 0.25);
    }
    
    .hidden-input {
        display: none;
    }
    
    .upload-item {
        margin: 10px 0;
        padding: 12px;
        border-radius: 6px;
        background-color: #f9f9f9;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
        transition: all 0.3s ease;
        display: flex;
        align-items: center;
    }
    
    .file-icon {
        margin-right: 10px;
        width: 24px;
        height: 24px;
        fill: #666;
    }
    
    .modern-progress {
        height: 6px;
        border-radius: 3px;
        overflow: hidden;
        background-color: #e0e0e0;
        margin: 8px 0;
        position: relative;
    }
    
    .progress-bar {
        height: 100%;
        background: linear-gradient(90deg, #0099ff, #33bbff);
        background-size: 200% 200%;
        animation: progress-animation 2s ease infinite;
        transition: width 0.3s ease;
        border-radius: 3px;
    }
    
    .completed {
        background: #4CAF50;
        animation: none;
    }
    
    .error {
        background: #f44336;
        animation: none;
    }
    
    .fade-out {
        opacity: 0;
        transform: translateY(-10px);
    }
</style>

<div data-name="dropzone" class="dropzone">
    <div data-name="upload_icon" class="upload-icon">
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
            <path d="M19.35 10.04C18.67 6.59 15.64 4 12 4 9.11 4 6.6 5.64 5.35 8.04 2.34 8.36 0 10.91 0 14c0 3.31 2.69 6 6 6h13c2.76 0 5-2.24 5-5 0-2.64-2.05-4.78-4.65-4.96zM14 13v4h-4v-4H7l5-5 5 5h-3z"/>
        </svg>
    </div>
    <p>Drag and drop files here or</p>
    <button data-name="button" class="file-button">Choose Files</button>
    <input data-name="file_input" type="file" multiple class="hidden-input">
</div>
<div data-name="uploads"></div>
        """

    def button__click(self, event):
        # When the button is clicked, trigger the file input
        self.file_input.click()

    def dropzone__dragover(self, event):
        # Prevent default to allow drop
        event.preventDefault()
        event.stopPropagation()
        # Add visual feedback
        self.dropzone.style.borderColor = '#0099ff'
        self.dropzone.style.backgroundColor = 'rgba(0, 153, 255, 0.1)'
        # Add animation
        self.upload_icon.style.animation = 'pulse 1s infinite'

    def dropzone__dragleave(self, event):
        event.preventDefault()
        event.stopPropagation()
        # Reset visual feedback
        self.dropzone.style.borderColor = '#ccc'
        self.dropzone.style.backgroundColor = 'rgba(245, 245, 245, 0.6)'
        self.upload_icon.style.animation = 'none'

    def dropzone__drop(self, event):
        event.preventDefault()
        event.stopPropagation()
        # Reset visual feedback
        self.dropzone.style.borderColor = '#ccc'
        self.dropzone.style.backgroundColor = 'rgba(245, 245, 245, 0.6)'
        self.upload_icon.style.animation = 'none'

        # Get files from the drop event
        files = event.dataTransfer.files
        self._process_files(files)

    def dropzone__click(self, event):
        # If they click the drop zone but not on the button or input, trigger the file input
        if event.target != self.file_input and event.target != self.button:
            self.file_input.click()

    def _process_files(self, files):
        # Process the files just like in the change event
        for file in files:
            progress = UploadProgressComponent()
            self.uploads.appendChild(progress.element)
            asyncio.create_task(upload_file(file, progress.update_progress))

    async def file_input__change(self, event):
        files = self.file_input.files
        self._process_files(files)
        self.file_input.value = ''


class UploadProgressComponent(wpc.Component):
    progress_container: js.HTMLElement = wpc.element()
    progress_bar: js.HTMLElement = wpc.element()
    file_name: js.HTMLElement = wpc.element()
    file_size: js.HTMLElement = wpc.element()
    file_icon: js.HTMLElement = wpc.element()
    status: js.HTMLElement = wpc.element()

    def init_component(self):
        # language=html
        self.element.innerHTML = """
<div class="upload-item">
    <div data-name="file_icon" class="file-icon">
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
            <path d="M14 2H6c-1.1 0-2 .9-2 2v16c0 1.1.9 2 2 2h12c1.1 0 2-.9 2-2V8l-6-6zm2 16H8v-2h8v2zm0-4H8v-2h8v2zm-3-5V3.5L18.5 9H13z"/>
        </svg>
    </div>
    <div style="flex-grow: 1;">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <div data-name="file_name" style="font-weight: 500; font-size: 14px;"></div>
            <div data-name="file_size" style="color: #666; font-size: 12px;"></div>
        </div>
        <div data-name="progress_container" class="modern-progress">
            <div data-name="progress_bar" class="progress-bar" style="width: 0%;"></div>
        </div>
        <div data-name="status" style="font-size: 12px; color: #666;"></div>
    </div>
</div>"""

    def _set_file_info(self, file: js.File):
        """Set the initial file information in the UI."""
        self.file_name.textContent = file.name

        # Format file size
        size_kb = file.size / 1024
        size_display = f"{size_kb:.1f} KB" if size_kb < 1024 else f"{size_kb / 1024:.1f} MB"
        self.file_size.textContent = size_display

        # Set file icon based on file type
        if file.type.startswith('image/'):
            self.file_icon.innerHTML = """
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
                    <path d="M21 19V5c0-1.1-.9-2-2-2H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2zM8.5 13.5l2.5 3.01L14.5 12l4.5 6H5l3.5-4.5z"/>
                </svg>
            """
        elif file.type.startswith('video/'):
            self.file_icon.innerHTML = """
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
                    <path d="M4 6.47L5.76 10H20v8H4V6.47M22 4h-4l2 4h-3l-2-4h-2l2 4h-3l-2-4H8l2 4H7L5 4H4c-1.1 0-2 .9-2 2v12c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V4z"/>
                </svg>
            """
        elif 'pdf' in file.type:
            self.file_icon.innerHTML = """
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
                    <path d="M20 2H8c-1.1 0-2 .9-2 2v12c0 1.1.9 2 2 2h12c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2zm-8.5 7.5c0 .83-.67 1.5-1.5 1.5H9v2H7.5V7H10c.83 0 1.5.67 1.5 1.5v1zm5 2c0 .83-.67 1.5-1.5 1.5h-2.5V7H15c.83 0 1.5.67 1.5 1.5v3zm4-3H19v1h1.5V11H19v2h-1.5V7h3v1.5zM9 9.5h1v-1H9v1zM4 6H2v14c0 1.1.9 2 2 2h14v-2H4V6zm10 5.5h1v-3h-1v3z"/>
                </svg>
            """

    def update_progress(self, progress: UploadProgress):
        """Callback function to update the UI with upload progress."""
        percentage = progress.percentage
        self.progress_bar.style.width = f"{percentage}%"

        if progress.starting:
            self._set_file_info(progress.file)

        if progress.completed:
            self.progress_bar.classList.add("completed")
            self.status.textContent = "Upload completed"
            self.status.style.color = "#4CAF50"
            self._fade_out()
        elif progress.failure:
            self.progress_bar.classList.add("error")
            self.status.textContent = f"Error: {progress.failure}"
            self.status.style.color = "#f44336"
        else:
            self.status.textContent = f"Uploading: {percentage}%"

    def _fade_out(self, fade_delay_secs=3):
        """Fade out and remove the progress element after completion."""

        async def _remove():
            await asyncio.sleep(1)  # Short delay before starting fade
            self.element.classList.add("fade-out")
            self.element.style.transition = f"all {fade_delay_secs}s ease"

            await asyncio.sleep(fade_delay_secs)
            self.element.remove()

        asyncio.create_task(_remove())


@dataclass
class UploadProgress:
    file: js.File
    bytes_uploaded: int
    total_bytes: int
    abort: bool = False  # Flag that can be set to stop the upload
    failure: Exception | None = None

    @property
    def starting(self) -> bool:
        return self.bytes_uploaded == 0

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


async def upload_file(
        file: js.File,
        progress_callback: Callable[[UploadProgress], None] = None,
        chunk_size: int = pow(2, 18)
) -> None:
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

        progress_callback(progress)  # Initial progress report

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
