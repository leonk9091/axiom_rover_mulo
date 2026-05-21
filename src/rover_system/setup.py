from setuptools import find_packages, setup

package_name = 'rover_system'

setup(
    name=package_name,
    version='1.0.0',
    packages=find_packages(),
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools', 'numpy', 'pyserial'],
    zip_safe=True,
    entry_points={
        'console_scripts': [
            'hardware_bridge = rover_system.nodes.hardware_bridge:main',
            'state_estimation = rover_system.nodes.state_estimation:main',
        ],
    },
)
