# Recipe CBR Generator
The goal of this project is to implement a Case-Based Reasoning (CBR) system for a cooking recipe generator using CBR. 
A Case-Based Reasoning (CBR) system is built on the principle that problems with similar characteristics often have comparable solutions. It relies on the idea that a previously successful solution can be effectively applied to a new, but similar, situation. Additionally, a CBR system is capable of modifying existing solutions to better fit the specifics of the current problem it faces.

Creators: Afek, Laura, Karl and Gerard

## Contents
This project contains the necessary folders and files to run the application Cooking Recipe generatopr.

The project is structured as follows:

    - documentation         [The folder contains a PDF report with the details about the CBR system and a User Manual PDF]
    - data                  [The folder contains the original dataset used in the project in CSV format, a processed version of the dataset, the case base in XML format, and the case library in XML format]
    - src                   [The folder contains the implementation of the CBR system, the GUI and the CLI tool, and some scripts to perform one time tasks like automatic testing and data preprocessing]
    - LICENSE               [The license of the project]
    - README.txt            [A README explaining the contents of the project]
    - requirements.txt      [The file contains the project dependencies to be installed]
    

## How to run the Cocktail CBR

### Prerequisites
You need to create a Python environment and install the required dependencies listed in the `requirements.txt` file inside `src/` 
with the following commands:

```python
python -m venv .venv
python -m pip install -r requirements.txt
```

### Running the WebAPP
To run the system using the GUI you can run:
```python
python src/cbr_app/app.py
```

In order to run the system using the CLI you can run:
```python
python src/cbr_app/cbr-cli.py
```

In order to run the tests you can run:
```python
python src/main_test.py
```



Test Example:
![image](https://github.com/Barathaner/Case-Based-Reasoning-System-Prototyp/assets/40422666/fa99b7fe-51aa-449b-b5d4-d3fae04a0df0)
