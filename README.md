# sonnet-generator

See slides at https://slides.com/janiceshiu/pycon-shakespeare-sonnets-python

To setup:

First install dependencies:

```
pip install -r requirements.txt
```

Then, make sure you have the dataset downloaded:

```
$ python
>>> import nltk
>>> nltk.download('gutenberg')
True
>>> nltk.download('brown')
True
```