import os
import re
import requests
import json
import fitz
import pandas as pd
import numpy as np
from tqdm.auto import tqdm
from spacy.lang.en import English
from sentence_transformers import SentenceTransformer, util
import torch
import textwrap

# 1. PDF Download/Check
PDF_PATH = r"D:\rag-from-scratch\Human-Nutrition-2020-Edition-1598491699.pdf"
PDF_URL = "https://pressbooks.oer.hawaii.edu/humannutrition2/open/download?type=pdf"

if not os.path.exists(PDF_PATH):
    print("File doesn't exist, downloading...")
    response = requests.get(PDF_URL)
    if response.status_code == 200:
        with open(PDF_PATH, "wb") as file:
            file.write(response.content)
        print(f"The file has been downloaded as {PDF_PATH}")
    else:
        raise RuntimeError(f"Failed to download the file: {response.status_code}")
else:
    print(f"File {PDF_PATH} exists")

# 2. PDF Reading and Text Extraction
def text_formatter(text: str) -> str:
    cleaned_text = text.replace("\n", " ").strip()
    return cleaned_text

def open_and_read_pdf(pdf_path: str) -> list[dict]:
    doc = fitz.open(pdf_path)
    pages_and_texts = []
    for page_number, page in tqdm(enumerate(doc)):
        text = page.get_text()
        text = text_formatter(text)
        pages_and_texts.append({
            "page_number": page_number - 41,  # adjust page numbers
            "page_char_count": len(text),
            "page_word_count": len(text.split(" ")),
            "page_sentence_count_raw": len(text.split(". ")),
            "page_token_count": len(text) / 4,
            "text": text
        })
    return pages_and_texts

# 3. Sentence Splitting and Chunking
def split_list(input_list: list, slice_size: int) -> list[list[str]]:
    return [input_list[i:i + slice_size] for i in range(0, len(input_list), slice_size)]

def process_pages(pages_and_texts, num_sentence_chunk_size=10):
    nlp = English()
    nlp.add_pipe("sentencizer")
    for item in tqdm(pages_and_texts):
        item["sentences"] = [str(s) for s in nlp(item["text"]).sents]
        item["page_sentence_count_spacy"] = len(item["sentences"])
        item["sentence_chunks"] = split_list(item["sentences"], num_sentence_chunk_size)
        item["num_chunks"] = len(item["sentence_chunks"])
    return pages_and_texts

def create_chunks(pages_and_texts):
    pages_and_chunks = []
    for item in tqdm(pages_and_texts):
        for sentence_chunk in item["sentence_chunks"]:
            chunk_dict = {}
            chunk_dict["page_number"] = item["page_number"]
            joined_sentence_chunk = "".join(sentence_chunk).replace("  ", " ").strip()
            joined_sentence_chunk = re.sub(r'\.([A-Z])', r'. \1', joined_sentence_chunk)
            chunk_dict["sentence_chunk"] = joined_sentence_chunk
            chunk_dict["chunk_char_count"] = len(joined_sentence_chunk)
            chunk_dict["chunk_word_count"] = len([word for word in joined_sentence_chunk.split(" ")])
            chunk_dict["chunk_token_count"] = len(joined_sentence_chunk) / 4
            pages_and_chunks.append(chunk_dict)
    return pages_and_chunks

# 4. Embedding Generation and Saving
def generate_and_save_embeddings(pages_and_chunks, min_token_length=30, model_name="all-mpnet-base-v2", device="cuda"):
    embedding_model = SentenceTransformer(model_name_or_path=model_name, device=device)
    df = pd.DataFrame(pages_and_chunks)
    pages_and_chunks_over_min_token_len = df[df["chunk_token_count"] > min_token_length].to_dict(orient="records")
    for item in tqdm(pages_and_chunks_over_min_token_len):
        item["embedding"] = embedding_model.encode(item["sentence_chunk"])
    text_chunks_and_embeddings_df = pd.DataFrame(pages_and_chunks_over_min_token_len)
    embeddings_df_save_path = "text_chunks_and_embeddings_df.csv"
    text_chunks_and_embeddings_df.to_csv(embeddings_df_save_path, index=False)
    return embeddings_df_save_path

# 5. Load Embeddings for Retrieval
def load_embeddings(embeddings_df_save_path, device="cuda"):
    text_chunks_and_embedding_df = pd.read_csv(embeddings_df_save_path)
    text_chunks_and_embedding_df["embedding"] = text_chunks_and_embedding_df["embedding"].apply(lambda x: np.fromstring(x.strip("[]"), sep=" "))
    pages_and_chunks = text_chunks_and_embedding_df.to_dict(orient="records")
    embeddings = torch.tensor(np.array(text_chunks_and_embedding_df["embedding"].tolist()), dtype=torch.float32).to(device)
    return pages_and_chunks, embeddings

# 6. Retrieval Functions
def print_wrapped(text, wrap_length=80):
    wrapped_text = textwrap.fill(text, wrap_length)
    print(wrapped_text)

def retrieve_relevant_resources(query: str, embeddings: torch.tensor, model: SentenceTransformer, n_resources_to_return: int=5, print_time: bool=True):
    query_embedding = model.encode(query, convert_to_tensor=True)
    from time import perf_counter as timer
    start_time = timer()
    dot_scores = util.dot_score(query_embedding, embeddings)[0]
    end_time = timer()
    if print_time:
        print(f"[INFO] Time taken to get scores on {len(embeddings)} embeddings: {end_time-start_time:.5f} seconds.")
    scores, indices = torch.topk(input=dot_scores, k=n_resources_to_return)
    return scores, indices

def print_top_results_and_scores(query: str, embeddings: torch.tensor, pages_and_chunks: list, model: SentenceTransformer, n_resources_to_return: int=5):
    scores, indices = retrieve_relevant_resources(query=query, embeddings=embeddings, model=model, n_resources_to_return=n_resources_to_return)
    print(f"Query: {query}\n")
    print("Results:")
    for score, index in zip(scores, indices):
        print(f"Score: {score:.4f}")
        print_wrapped(pages_and_chunks[index]["sentence_chunk"])
        print(f"Page number: {pages_and_chunks[index]['page_number']}")
        print("\n")

# 7. LLM Answer Generation (Ollama Llama2 via REST API, streaming)
def generate_answer_with_llama2_ollama(query, indices, pages_and_chunks, model_name="llama2"):
    context = "\n".join([pages_and_chunks[idx]["sentence_chunk"] for idx in indices])
    prompt = f"Context:\n{context}\n\nQuestion: {query}\nAnswer:"
    url = "http://localhost:11434/api/chat"
    payload = {
        "model": model_name,
        "messages": [
            {"role": "user", "content": prompt}
        ]
    }
    response = requests.post(url, json=payload, stream=True)
    response.raise_for_status()
    answer = ""
    for line in response.iter_lines():
        if line:
            data = json.loads(line)
            if "message" in data and "content" in data["message"]:
                answer += data["message"]["content"]
    return answer.strip()

# 8. Main block for running the pipeline
if __name__ == "__main__":
    # Step 1: PDF to text
    pages_and_texts = open_and_read_pdf(PDF_PATH)
    # Step 2: Sentence splitting and chunking
    pages_and_texts = process_pages(pages_and_texts)
    pages_and_chunks = create_chunks(pages_and_texts)
    # Step 3: Embedding generation and saving
    embeddings_df_save_path = generate_and_save_embeddings(pages_and_chunks)
    # Step 4: Load embeddings
    pages_and_chunks, embeddings = load_embeddings(embeddings_df_save_path)
    # Step 5: Load embedding model for retrieval
    embedding_model = SentenceTransformer(model_name_or_path="all-mpnet-base-v2", device="cuda")
    # Step 6: Example query and answer generation using Ollama Llama2
    query = "What are the macronutrients, and what roles do they play in the human body?"
    scores, indices = retrieve_relevant_resources(query=query, embeddings=embeddings, model=embedding_model, n_resources_to_return=5)
    answer = generate_answer_with_llama2_ollama(query=query, indices=indices, pages_and_chunks=pages_and_chunks, model_name="llama2")
    print("Query:", query)
    print("\nAnswer:", answer) 