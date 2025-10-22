import cv2
import numpy as np
from io import BytesIO
from pathlib import Path
from PIL import Image


def hdr_to_preview(
    input_path: str | Path,
    gamma: float = 2.2,
    intensity: float = 0.0,
    light_adapt: float = 1.0,
    color_adapt: float = 0.0,
    as_image: bool = True,
    as_bytes: bool = False,
) -> Image.Image | np.ndarray | bytes:
    """Load an HDR image, tone-map it, and return a preview representation.

    This function loads a 32-bit HDR environment map, applies Reinhard tone
    mapping, and produces a low dynamic range version suitable for previews.

    Args:
        input_path (str | Path): Path to the HDR image.
        gamma (float, optional): Gamma correction factor. Defaults to 2.2.
        intensity (float, optional): Reinhard tone-mapping intensity. Defaults to 0.0.
        light_adapt (float, optional): Light adaptation factor. Defaults to 1.0.
        color_adapt (float, optional): Color adaptation factor. Defaults to 0.0.
        as_image (bool, optional): If True, return a Pillow Image.
        as_bytes (bool, optional): If True, return JPEG bytes (e.g. for web display).

    Returns:
        Union[Image.Image, np.ndarray, bytes]:
            - Pillow `Image` if `as_image` is True.
            - NumPy array (H×W×3, uint8) if both flags are False.
            - JPEG byte stream if `as_bytes` is True.

    Raises:
        FileNotFoundError: If the HDR file cannot be loaded.
    """
    input_path = Path(input_path)

    hdr = cv2.imread(str(input_path), cv2.IMREAD_ANYDEPTH)
    if hdr is None:
        raise FileNotFoundError(f"Cannot read HDR image: {input_path}")

    tonemap = cv2.createTonemapReinhard(
        gamma=gamma,
        intensity=intensity,
        light_adapt=light_adapt,
        color_adapt=color_adapt,
    )

    ldr = tonemap.process(hdr)
    ldr_8bit = np.clip(ldr * 255, 0, 255).astype(np.uint8)
    ldr_rgb = cv2.cvtColor(ldr_8bit, cv2.COLOR_BGR2RGB)

    if as_bytes:
        # Encode to in-memory JPEG
        img = Image.fromarray(ldr_rgb)
        buffer = BytesIO()
        img.save(buffer, format="JPEG", quality=85)
        return buffer.getvalue()

    if as_image:
        return Image.fromarray(ldr_rgb)
    else:
        return ldr_rgb
