from setuptools import find_packages, setup

package_name = 'rover_safety'

setup(
    name=package_name,
    version='1.0.0',
    packages=find_packages(),
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools', 'pyserial'],
    zip_safe=True,
    entry_points={
        'console_scripts': [
            'safety_watchdog = rover_safety.nodes.safety_watchdog:main',
            'stability_margin = rover_safety.nodes.stability_margin:main',
        ],
    },
)
