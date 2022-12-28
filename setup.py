from setuptools import find_packages, setup

setup(
    name='demo_utils_yc_test',
    version='1.0.5',
    install_requires=(
        'setuptools',
        'webexteamssdk==1.6.1',
    ),
    include_package_data=True,
    packages=find_packages(),
)
