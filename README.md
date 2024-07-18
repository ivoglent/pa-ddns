# Simple DDNS service
Dynamic DNS bot which can update domain's IP hosted by PA Vietnam

## Requirements
`Python 3.10`

## Config
Update deps:
``` 
pip3 install -r requirements.txt
```

Create config file like:
``` 
[
    {
        "domain": "domain-name",
        "password": "password",
        "entries": ["@", "subdomain"]
    }
]
```
and put it to ~/.paddns

then simply run:
``` 
python main.py
```

