# -*- coding: utf-8 -*-
"""Tokenizacion.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1xo1nxTSXVyiPSNx2uTa-Es2mh4hwTqYf

<h1>Importamos los corpus</h1>
<h4>Brown</h4>
"""

import nltk
import re
from nltk.corpus import brown
from collections import Counter

nltk.download('brown')
brown_complete = [word for word in brown.words() if re.match("\w", word)]

"""<h4>Axolotl</h4>"""

!pip install elotl

import elotl.corpus
axolotl_corpus = elotl.corpus.load("axolotl")

import math

def calculate_entropy(corpus: list[str]) -> float:
    words_counts = Counter(corpus)
    total_words = len(corpus)
    probabilities = {word: count / total_words for word, count in words_counts.items()}
    entropy = -sum(p * math.log2(p) for p in probabilities.values())
    return entropy

"""<h1>Entropía con tokenización word-level</h1>"""

brown_corpus = brown_complete[:100000] #para usar solo un subset de la monstruosidad que es el brown
h_brown_wl = calculate_entropy(brown_corpus)
print("La entropía del corpus brown haciendo tokenización word-level es: ", h_brown_wl)

axolotl_words = [word for row in axolotl_corpus for word in row[1].lower().split()]
h_axolotl_wl = calculate_entropy(axolotl_words)
print("La entropía del corpus axolotl haciendo tokenización word-level es: ", h_axolotl_wl)

"""<h1>Entropía con tokenización BPE"""

!pip install subword-nmt

CORPORA_PATH = "tokenization/"

def write_plain_text_corpus(raw_text: str, file_name: str) -> None:
    with open(f"{file_name}.txt", "w") as f:
        f.write(raw_text)

train_rows_count = len(axolotl_words) - round(len(axolotl_words)*.30)

axolotl_train = axolotl_words[:train_rows_count]
axolotl_test = axolotl_words[train_rows_count:]

write_plain_text_corpus(" ".join(axolotl_train), CORPORA_PATH + "axolotl_plain")

!subword-nmt learn-bpe -s 500 < tokenization/axolotl_plain.txt > tokenization/axolotl.model

write_plain_text_corpus(" ".join(axolotl_test), CORPORA_PATH + "axolotl_plain_test")

!subword-nmt apply-bpe -c tokenization/axolotl.model < tokenization/axolotl_plain_test.txt > tokenization/axolotl_tokenized.txt

with open(CORPORA_PATH + "axolotl_tokenized.txt") as f:
    axolotl_test_tokenized = f.read().split()

axolotl_test_tokenized_types = Counter(axolotl_test_tokenized)
axolotl_test_tokenized_types.most_common(20)

h_axolotl_bpe = calculate_entropy(axolotl_test_tokenized)
print("La entropía del corpus axolotl con bpe tokenization: ", h_axolotl_bpe)

train_rows_count_brown = len(brown_corpus) - round(len(brown_corpus)*.30)

brown_train = brown_corpus[:train_rows_count_brown]
brown_test = brown_corpus[train_rows_count_brown:]

write_plain_text_corpus(" ".join(brown_train), CORPORA_PATH + "brown_plain")

!subword-nmt learn-bpe -s 500 < tokenization/brown_plain.txt > tokenization/brown.model

write_plain_text_corpus(" ".join(brown_test), CORPORA_PATH + "brown_plain_test")

!subword-nmt apply-bpe -c tokenization/brown.model < tokenization/brown_plain_test.txt > tokenization/brown_tokenized.txt

with open(CORPORA_PATH + "brown_tokenized.txt") as f:
    brown_test_tokenized = f.read().split()

brown_test_tokenized_types = Counter(brown_test_tokenized)
brown_test_tokenized_types.most_common(20)

h_brown_bpe = calculate_entropy(brown_test_tokenized)
print("La entropía del corpus brown con bpe tokenization: ", h_brown_bpe)

"""<h1>Entropías</h1>
Listadas de nuevo para poder visualizarlas mejor:

<h3>Corpus Brown</h3>
Con word-level
"""

print(h_brown_wl)

"""Con BPE"""

print(h_brown_bpe)

"""<h3> Corpus Axolotl </h3>
Con word level
"""

print(h_axolotl_wl)

"""Con BPE"""

print(h_axolotl_bpe)

"""<h1> Preguntas </h1>
<h3>¿Aumento o disminuyó la entropia para los corpus?</h3>
Para ambos corpus, su versión tokenizada con BPE bajo considerablemente, especialmente con axolotl, donde con word-level tokenization teníamos una entropía de 11.84 y logramos reducirla hacia 8.35

<h3>¿Qué significa que la entropía aumente o disminuya en un texto?</h3>
Significa que el grado de impredictibilidad, en el caso de la lengua, al aumentar la entropía significa que es más impredecible, es decir, más rica en vocabulario, que aunque puede ser muy interesante desde un punto de vista lingüistico, a la hora de querer hacer programas nos puede causar problemas que sea tan rica ya que hay muchas cosas que pueden salir de lo que se consideraría la norma y es más difícil de procesar.

<h3>¿Como influye la tokenizacion en la entropía de un texto?</h3>
Hace que disminuya la entropía para que el procesamiento de textos se vuelva una tarea un poquiiiito más sencilla.

<h1>
"""