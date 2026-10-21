from glob import glob
from setuptools import find_packages, setup


package_name = "competition_teleop"

setup(
    name=package_name,
    version="0.1.0",
    packages=find_packages(exclude=["test"]),
    data_files=[
        ("share/ament_index/resource_index/packages", ["resource/" + package_name]),
        ("share/" + package_name, ["package.xml"]),
        ("share/" + package_name + "/config", glob("config/*.yaml")),
        ("share/" + package_name + "/launch", glob("launch/*.py")),
    ],
    install_requires=["setuptools"],
    zip_safe=True,
    maintainer="Karim",
    maintainer_email="g202521230@kfupm.edu.sa",
    description="Safe PS5 teleoperation for the competition simulator.",
    license="MIT",
    entry_points={
        "console_scripts": [
            "ps5_teleop = competition_teleop.ps5_teleop_node:main",
        ],
    },
)