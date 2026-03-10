from setuptools import find_packages, setup

package_name = 'autonomous_patrol_system'

setup(
    name=package_name,
    version='0.2.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        # Required by ament_index
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        # Package manifest
        ('share/' + package_name, ['package.xml']),
        
        # ✅ Launch files
        ('share/' + package_name + '/launch', [
            'launch/cyclic_patrol.launch.py',
        ]),
        
        # ✅ Config files 
        ('share/' + package_name + '/config', [
            'config/waypoints.yaml',
        ]),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Yasseene',
    maintainer_email='RAHAL.Mohamed-Yassine@tek-up.de',
    description='Autonomous patrol system for TurtleBot4',
    license='Apache-2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'cyclic_patrol = autonomous_patrol_system.cyclic_patrol_node:main',
        ],
    },
)