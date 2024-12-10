from setuptools import setup

setup(name='gridworlds',
      version='0.1',
      description='Minimal gridworlds for simple reinforcement learning',
      url='https://gitlab.mi.hdm-stuttgart.de/theodoridis/gridworlds',
      author='Johannes Theodoridis',
      author_email='theodoridis@hdm-stuttgart.de',
      license='MIT',
      packages=['gridworlds'],
      install_requires=[
          'pygame',
      ],
      zip_safe=False)
