from setuptools import find_packages, setup

package_name = 'autonomous_patrol_system'

setup(
    name=package_name,
    version='0.2.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        ('share/' + package_name + '/launch', [
            'launch/cyclic_patrol.launch.py',
        ]),
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
            'environment_monitor = autonomous_patrol_system.environment_monitor_node:main',
            'evidence_capture = autonomous_patrol_system.evidence_capture_node:main',
            'alert_dispatcher = autonomous_patrol_system.alert_dispatcher_node:main',
            'cli_feedback = autonomous_patrol_system.cli_feedback_node:main',
            'mission_controller = autonomous_patrol_system.mission_controller_node:main',
        ],
    },
)