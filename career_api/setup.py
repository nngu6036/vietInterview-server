from setuptools import setup, find_packages

setup(
        name='career_api',
        version='3.0.3',
        long_description=__doc__,
        packages=find_packages(),
        include_package_data=True,
        zip_safe=False,
        install_requires=[
            'Flask',
            'flask_cors',
            'phonenumbers',
            'erppeek'
        ]
)
