from setuptools import find_packages, setup

package_name = 'automated_patrol_state_machine'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(include=[
    'automated_patrol_state_machine',
    'automated_patrol_state_machine.*'
]),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='yass',
    maintainer_email='RAHAL.Mohamed-Yassine@tek-up.de',
    description='TODO: Package description',
    license='TODO: License declaration',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
    'console_scripts': [
        'patrol_executor_node = automated_patrol_state_machine.nodes.patrol_executor_node:main',
    ],
    },

)
