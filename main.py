"""
Algorithm server definition.
Documentation: https://github.com/Imaging-Server-Kit/cookiecutter-serverkit
"""

from typing import List, Type
from pathlib import Path
import numpy as np
from pydantic import BaseModel, Field, field_validator
import uvicorn
import skimage.io
import imaging_server_kit as serverkit
import spam.DIC
import spam.deformation


class Parameters(BaseModel):
    """Defines the algorithm parameters"""

    moving_image: str = Field(
        ...,
        title="Moving image",
        description="Moving image (2D, 3D).",
        json_schema_extra={"widget_type": "image"},
    )

    fixed_image: str = Field(
        ...,
        title="Fixed image",
        description="Fixed image (2D, 3D).",
        json_schema_extra={"widget_type": "image"},
    )

    @field_validator("moving_image", mode="after")
    def decode_moving_image_array(cls, v) -> np.ndarray:
        image_array = serverkit.decode_contents(v)
        if image_array.ndim not in [2, 3]:
            raise ValueError("Array has the wrong dimensionality.")
        return image_array

    @field_validator("fixed_image", mode="after")
    def decode_fixed_image_array(cls, v) -> np.ndarray:
        image_array = serverkit.decode_contents(v)
        if image_array.ndim not in [2, 3]:
            raise ValueError("Array has the wrong dimensionality.")
        return image_array


class SpamRegisterServer(serverkit.AlgorithmServer):
    def __init__(
        self,
        algorithm_name: str = "spam",
        parameters_model: Type[BaseModel] = Parameters,
    ):
        super().__init__(algorithm_name, parameters_model)

    def run_algorithm(
        self, moving_image: np.ndarray, fixed_image: np.ndarray, **kwargs
    ) -> List[tuple]:
        """Runs the spam-reg algorithm."""
        reg = spam.DIC.register(moving_image, fixed_image)
        phi = reg.get("Phi")
        registered_image = spam.DIC.applyPhiPython(moving_image, Phi=phi)

        image_params = {"name": "Registered image"}

        return [(registered_image, image_params, "image")]

    def load_sample_images(self) -> List["np.ndarray"]:
        """Loads one or multiple sample images."""
        image_dir = Path(__file__).parent / "sample_images"
        images = [skimage.io.imread(image_path) for image_path in image_dir.glob("*")]
        return images


server = SpamRegisterServer()
app = server.app

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000)
