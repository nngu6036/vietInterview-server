from setuptools import setup, find_packages

setup(
        name='career_socket',
        version='1.0.2',
        long_description=__doc__,
        packages=find_packages(),
        include_package_data=True,
        package_data = {'career_socket':['templates/*']},
        zip_safe=False,
        install_requires=[
            'Flask',
            'phonenumbers',
            'flask-socketio',
            'erppeek'
        ]
)
