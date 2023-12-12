from setuptools import setup, find_packages

setup(
    name='generator',
    version='1.0.0',
    packages=find_packages(),  # Автоматически находит все пакеты внутри вашего пакета
    # Другая мета-информация о вашем пакете, например, автор, описание, зависимости и т. д.
    author='Your Name',
    author_email='your@email.com',
    description='Description of your package',
    install_requires=[],  # Зависимости вашего пакета
)