from setuptools import find_packages, setup

package_name = 'rover_navigation'

setup(
    name=package_name,
    version='1.0.0',
    packages=find_packages(),
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools', 'numpy', 'filterpy'],
    zip_safe=True,
    entry_points={
        'console_scripts': [
            'follow_me = rover_navigation.nodes.follow_me:main',
            'shared_autonomy = rover_navigation.nodes.shared_autonomy:main',
            'terrain_assessor = rover_navigation.nodes.terrain_assessor:main',
        ],
    },
)
