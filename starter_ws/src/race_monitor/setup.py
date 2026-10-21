from glob import glob
from setuptools import find_packages, setup


package_name = "race_monitor"

setup(
    name=package_name,
    version="0.1.0",
    packages=find_packages(exclude=["test"]),
    data_files=[
        ("share/ament_index/resource_index/packages", ["resource/" + package_name]),
        ("share/" + package_name, ["package.xml"]),
        ("share/" + package_name + "/config", glob("config/*.yaml")),
    ],
    install_requires=["setuptools"],
    zip_safe=True,
    maintainer="Karim",
    maintainer_email="g202521230@kfupm.edu.sa",
    description="Lap timing and race status for the competition simulator.",
    license="MIT",
    entry_points={
        "console_scripts": [
            "race_monitor = race_monitor.race_monitor_node:main",
        ],
    },
)