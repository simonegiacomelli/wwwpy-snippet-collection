import logging
from pathlib import Path

logger = logging.getLogger(__name__)


async def save_file(filename: str, content: bytes) -> None:
    # log the information about the file being saved, about the content log only the length
    logger.info(f'save_file `{filename}` with content length {len(content)}')
    file = _resolve_file(filename)
    file.write_bytes(content)


def _resolve_file(name: str) -> Path:
    folder = Path(__file__).parent.parent / 'uploads'
    candidate = folder / name
    # security check: candidate is inside the folder?
    if not candidate.resolve().is_relative_to(folder.resolve()):
        raise ValueError(f'Invalid path: {candidate}')
    candidate.parent.mkdir(parents=True, exist_ok=True)
    return candidate

