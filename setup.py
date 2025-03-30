from setuptools import setup, find_packages

setup(
    name="journalapi",
    version="0.1.0",
    description="A Flask-based journaling API with JWT authentication and sentiment tagging.",
    author="Your Name",
    author_email="your.email@example.com",
    packages=find_packages(exclude=["tests", "instance"]),
    include_package_data=True,
    install_requires=[
        "Flask",
        "Flask-JWT-Extended",
        "Flask-RESTful",
        "Flask-SQLAlchemy",
        "Werkzeug",
    ],
    entry_points={
        "console_scripts": [
            "pwp-journalapi=pwp_journalapi.app:create_app"
        ]
    },
    python_requires='>=3.7',
)
