from setuptools import setup, find_packages

setup(
    name="pwp_journalapi",
    version="0.1.0",
    description="A Flask RESTful journaling API.",
    author="Your Name",
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        "flask",
        "flask-restful",
        "flask-sqlalchemy",
        "flask-jwt-extended",
        "werkzeug"
    ],
    python_requires='>=3.7',
)