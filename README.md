
![Logo](https://avatars.githubusercontent.com/u/10178994?s=200)
# Load test
Just run the application and measure the performance.


## Authors

- [@prabalPathak](https://www.github.com/prabal01pathak)


## Running Tests

To run tests, run the following command

```bash
  pytest
```


## Usage/Examples

```python3
python3 run_process.py 

or 

python3 run_process.py --help (to see the cli arguments)
```

## Lessons Learned
Practice Makes Perfect
## 🛠 Skills
- Python3
- multiprocessing
- threading
- typer
- bash
- machine learning
- object-detection
- pytest
- cli


## Tech Stack
**Programming Language** - Python3

**Framework** - Typer

**python Multiprocessing**

**python multithreading**

## Usage

#### start single process

```http
  python3 run_process.py
```

| Parameter | Type     | Description                |
| :-------- | :------- | :------------------------- |
| --process_count| `int`| **optional** |
| --thread_count| `int`| **optional** |
|--run_time| `int`| **optional** (in seconds) |
| --create-log| `int`| **optional**(--no-run-detections to do it false) |
| --run-detections| `int`| **optional**(--no-run-detections to do it false) |

## Documentation

[Documentation](https://linktodocumentation)


## Features

- run object detections/don't run
- build analytics
- command line interface
- Cross Platform


## Installation

Install my-project with npm

```bash
  pip3 install poetry
  poetry shell
  poetry install
```
    
## License

[MIT](https://choosealicense.com/licenses/mit/)


## Run Locally

Clone the project

```bash
  git clone https://github.com/prabal01pathak/load_testing.git
```

Go to the project directory

```bash
  cd load_testing
```

Install dependencies

```
poetry install
```

start the combinations of process and threads

```bash
python3 run_combinations.py 

or

python3 run_combinations.py --help (for mode details)
```

