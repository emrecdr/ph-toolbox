# Helper Functions Package

## Installation
```shell
 pipenv install
```

```shell
 export PYTHONPATH="${HOME}/Projects/pypi/ph_toolbox"
```

## Testing
``` shell
make test
```

```shell
 pipenv run pytest ./tests/
```

Or specific test:

```shell
 pipenv run pytest ./tests/ph_toolbox/test_config.py
```

## Running

Can be installed from https://pypi.org/project/ph-toolbox/

```shell
pipenv install ph-toolbox
```

Then can be imported into python code like below

```
from ph_toolbox.config import Config
from ph_toolbox.utils import get_logger
```
