import setuptools

setuptools.setup(
    name="NFC-Playlist",
    version="0.1.0",
    url="https://github.com/wingesas/nfc-playlist",

    author="wingesas",
    author_email="wingesas@gmail.com",

    description="NFC-Playlist",
    long_description=open('README.rst').read(),

    packages=setuptools.find_packages(),

    install_requires=[
        'setuptools',
        'nxppy >= 1.3.2',
        'python-mpd2 >= 0.5.4'
    ],

    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Programming Language :: Python :: 2.7',
    ],
)
