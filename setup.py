from setuptools import setup, find_packages

VERSION = '0.0.1' 
DESCRIPTION = 'TAPGDC: Fitting a generalized diffusion curve and managing TAP data'
LONG_DESCRIPTION = 'A collection of methods for analyzing Temporal Analysis of Products (TAP) reactor data.'

# Setting up
# to create documentation (in docs) -> sphinx-aipdoc -o . .. -> make clean -> make html
# initial build of docs -> sphinx-build -M html docs/source/ docs/build
setup(
        name="tapgdc", 
        version=VERSION,
        author="M. Ross Kunz",
        author_email="<rosskunz@gmail.com>",
        description=DESCRIPTION,
        long_description=LONG_DESCRIPTION,
        packages=find_packages(),
        install_requires=['numpy', 'pandas', 'nptdms', 'pyarrow', 'duckdb'], 
        
        keywords=['TAP', 'Temporal Analysis of Products', 'gdc'],
        classifiers= [
            "Development Status :: 3 - Alpha",
            "Intended Audience :: Science",
            "Programming Language :: Python :: 3",
            "Operating System :: MacOS :: MacOS X",
            "Operating System :: Microsoft :: Windows",
        ],
        include_package_data=False
)