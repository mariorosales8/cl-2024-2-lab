# -*- coding: utf-8 -*-
"""practica08.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1JLa8P16SrUBTXGQO0wpUwanoDBbK62gm

# Practica 07

Alumno: David Pérez Jacome \\
Número de Cuenta: 316330420

**Actividades**

1. Construir un modelo del lenguaje neuronal a partir de un corpus en español
  - Corpus: El Quijote. URL: https://www.gutenberg.org/ebooks/2000
  - **NOTA: Considera los recursos de computo. Recuerda que en la practica utilizamos ~50k oraciones**
  - Modelo de trigramas con n = 3
  - Incluye informacion sobre setup de entrenamiento:
    - Dimension de embeddings
    - Dimsension de capa oculta
    - Cantidad de oraciones para entrenamiento
    - Batch size y context size
  - Incluye la liga de drive de tu modelo
2. Imprima en pantalla un tres ejemplos de generacion de texto
  - Proponga mejoras en las estrategias de generación de texto vistas en la práctica
  - Decriba en que consiste la estrategia propuesta
  - Compare la estrategia de la práctica y su propuesta

Paso 1. Construir el modelo de lenguaje neuronal
"""

import requests

url = "https://www.gutenberg.org/files/2000/2000-0.txt"
response = requests.get(url)
quijote_text = response.text

# Guardar el texto en un archivo local
with open("el_quijote.txt", "w", encoding="utf-8") as f:
    f.write(quijote_text)

import requests
import re
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader

# Función para descargar archivos
def download_file(url, file_name):
    with open(file_name, "wb") as f:
        response = requests.get(url)
        f.write(response.content)

# Descargar el corpus
url = "https://www.gutenberg.org/files/2000/2000-0.txt"
download_file(url, "el_quijote.txt")

# Leer el texto
with open("el_quijote.txt", "r", encoding="utf-8") as f:
    quijote_text = f.read()

# Preprocesamiento del texto
def preprocess_text(text):
    text = re.sub(r'\s+', ' ', text)  # Reemplazar múltiples espacios por uno
    sentences = re.split(r'[.!?]', text)  # Dividir en oraciones
    sentences = [sentence.strip() for sentence in sentences if len(sentence) > 0]
    return sentences[:50000]  # Limitar a 50k oraciones

# Crear dataset
class TrigramDataset(Dataset):
    def __init__(self, sentences):
        self.trigrams = []
        self.vocab = set()
        for sentence in sentences:
            words = sentence.split()
            self.vocab.update(words)
            self.trigrams.extend([(words[i], words[i+1], words[i+2]) for i in range(len(words) - 2)])
        self.vocab = list(self.vocab)
        self.word_to_idx = {word: idx for idx, word in enumerate(self.vocab)}
        self.idx_to_word = {idx: word for word, idx in self.word_to_idx.items()}

    def __len__(self):
        return len(self.trigrams)

    def __getitem__(self, idx):
        trigram = self.trigrams[idx]
        return (torch.tensor([self.word_to_idx[trigram[0]], self.word_to_idx[trigram[1]]], dtype=torch.long),
                torch.tensor(self.word_to_idx[trigram[2]], dtype=torch.long))

# Definir el modelo
class TrigramModel(nn.Module):
    def __init__(self, vocab_size, embedding_dim, hidden_dim):
        super(TrigramModel, self).__init__()
        self.embeddings = nn.Embedding(vocab_size, embedding_dim)
        self.linear1 = nn.Linear(embedding_dim * 2, hidden_dim)
        self.linear2 = nn.Linear(hidden_dim, vocab_size)

    def forward(self, inputs):
        embeds = self.embeddings(inputs).view(inputs.size(0), -1)  # Reformar a (batch_size, embedding_dim * context_size)
        out = torch.relu(self.linear1(embeds))
        out = self.linear2(out)
        log_probs = torch.log_softmax(out, dim=1)
        return log_probs

# Configuración de entrenamiento
embedding_dim = 50
hidden_dim = 100
batch_size = 64
context_size = 2
learning_rate = 0.01
num_epochs = 5

# Preprocesar el texto
sentences = preprocess_text(quijote_text)

# Crear dataset y dataloader
dataset = TrigramDataset(sentences)
dataloader = DataLoader(dataset, batch_size=batch_size, shuffle=True)

# Instanciar el modelo
model = TrigramModel(len(dataset.vocab), embedding_dim, hidden_dim)
criterion = nn.NLLLoss()
optimizer = optim.SGD(model.parameters(), lr=learning_rate)

# Entrenamiento
for epoch in range(num_epochs):
    total_loss = 0
    for context, target in dataloader:
        optimizer.zero_grad()
        log_probs = model(context)
        loss = criterion(log_probs, target)
        loss.backward()
        optimizer.step()
        total_loss += loss.item()
    print(f"Epoch {epoch+1}, Loss: {total_loss/len(dataloader)}")

# Guardar el modelo
torch.save(model.state_dict(), "trigram_model.pth")

# Función para generar texto
def generate_text(model, dataset, initial_words, max_len=20):
    model.eval()
    words = initial_words
    for _ in range(max_len - len(words)):
        context = torch.tensor([dataset.word_to_idx[w] for w in words[-2:]], dtype=torch.long).unsqueeze(0)
        with torch.no_grad():
            log_probs = model(context)
        word_idx = torch.argmax(log_probs, dim=1).item()
        words.append(dataset.idx_to_word[word_idx])
        if words[-1] == '<eos>':
            break
    return ' '.join(words)

# Ejemplos de generación
initial_words = ["En", "un"]
print(generate_text(model, dataset, initial_words))

initial_words = ["Don", "Quijote"]
print(generate_text(model, dataset, initial_words))

initial_words = ["Sancho", "Panza"]
print(generate_text(model, dataset, initial_words))

# Generación de texto con sampling
def generate_text_with_sampling(model, dataset, initial_words, max_len=20):
    model.eval()
    words = initial_words
    for _ in range(max_len - len(words)):
        context = torch.tensor([dataset.word_to_idx[w] for w in words[-2:]], dtype=torch.long).unsqueeze(0)
        with torch.no_grad():
            log_probs = model(context)
        word_idx = torch.multinomial(torch.exp(log_probs), num_samples=1).item()
        words.append(dataset.idx_to_word[word_idx])
        if words[-1] == '<eos>':
            break
    return ' '.join(words)

# Ejemplos de generación con sampling
initial_words = ["En", "un"]
print(generate_text_with_sampling(model, dataset, initial_words))

initial_words = ["Don", "Quijote"]
print(generate_text_with_sampling(model, dataset, initial_words))

initial_words = ["Sancho", "Panza"]
print(generate_text_with_sampling(model, dataset, initial_words))