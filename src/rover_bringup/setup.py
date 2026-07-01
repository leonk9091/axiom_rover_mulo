import os
from glob import glob

from setuptools import setup

package_name = "rover_bringup"

setup(
    name=package_name,
    version="1.0.0",
    packages=[],
    data_files=[
        ("share/ament_index/resource_index/packages", ["resource/" + package_name]),
        ("share/" + package_name, ["package.xml"]),
        ("share/" + package_name + "/launch", glob("launch/*.launch.py")),
        (
            "share/" + package_name + "/config",
            [os.path.join("..", "..", "config", "rover_params.yaml")],
        ),
        (
            "share/" + package_name + "/config/profiles",
            glob(os.path.join("..", "..", "config", "profiles", "*.yaml")),
        ),
    ],
    install_requires=["setuptools"],
    zip_safe=True,
)

