#!/usr/bin/env python3

import re
import os
import shutil
import urllib.request
import pandas as pd 

from nltk.tokenize import sent_tokenize, word_tokenize


sentence_id = 0


def download_txt(document_url, out_name):
    """ Download a given text document from the web """
    with urllib.request.urlopen(document_url) as response, open(out_name, 'wb') as out_file:
        shutil.copyfileobj(response, out_file)


def get_contents(lines):
    """ Get the contents from the bible document """
    old_testament = []
    new_testament = []

    testament = "old"
    for num, line in enumerate(lines[106:189]):
        clean_line = line.strip().split(",")[0]

        if clean_line == "The New Testament":
            testament = "new"
            continue

        if clean_line != "":
            section = ""
            if testament == "old":
                if clean_line == "First Book of Samuel":
                    section = "THE FIRST BOOK OF SAMUEL, OTHERWISE CALLED THE FIRST BOOK OF KINGS"
                elif clean_line == "Second Book of Samuel":
                    section = "THE SECOND BOOK OF KINGS"
                elif clean_line == "Book of Nehemias":
                    section = "THE BOOK OF NEHEMIAS, WHICH IS CALLED THE SECOND OF ESDRAS"
                elif clean_line in ["Solomon's Canticle of Canticles", "Ecclesiastes", "Ecclesiasticus"]:
                    section = f"{clean_line.upper()}"
                else:
                    section = f"THE {clean_line.upper()}"
                old_testament.append(section)
            else:
                if "Gospel According to " in clean_line:
                    apostel = clean_line.replace("Gospel ", "").replace(
                        "St.", "Saint") if "Matthew" in clean_line else clean_line.replace("Gospel ", "")
                    section = f"THE HOLY GOSPEL OF JESUS CHRIST {apostel.upper()}"
                elif clean_line == "Epistle of St. Paul to the Romans":
                    section = "THE EPISTLE OF ST. PAUL THE APOSTLE TO THE ROMANS"
                elif clean_line == "Catholic Epistle of St. Jude the Apostle":
                    section = "THE CATHOLIC EPISTLE OF ST. JUDE"
                else:
                    section = f"THE {clean_line.upper()}"
                new_testament.append(section)

    return old_testament, new_testament


def delete_empty_lines(lines):
    """ Delete all lines that are empty """
    return [line for line in lines if line.strip() != ""]


def delete_meta(lines):
    """ Delete any lines that are not part of the actual content """
    for num, line in enumerate(lines):
        if line.startswith("*** START"):
            start_index = num
        if line.startswith("*** END"):
            end_index = num
            break

    return delete_empty_lines(lines[start_index + 1: end_index])


def split_testaments(lines):
    """ Split the lines into the two testaments """
    start_line = "THE BOOK OF GENESIS"
    split_line = "THE NEW TESTAMENT"
    end_line = "*** END OF THE PROJECT GUTENBERG EBOOK THE BIBLE, DOUAY-RHEIMS VERSION ***"

    for num, line in enumerate(lines):
        if line.strip() == start_line:
            start_idx = num
        elif line.strip() == split_line:
            split_idx = num
        elif line.strip() == end_line:
            end_idx = num
            break

    return delete_empty_lines(lines[start_idx: split_idx]), delete_empty_lines(lines[split_idx: end_idx])


def get_books(toc, testament):
    """ Get the indices for the books """
    books = {}
    prev_idx = 0

    for num, section in enumerate(toc):
        if num != 0:
            previous_section = toc[num-1]
        for i in range(prev_idx, len(testament)):
            if section == testament[i].strip():
                books[section] = [i]
                if num != 0:
                    books[section] = [i]
                    books[previous_section].append(i)
                if num == len(toc)-1:
                    books[section].append(len(testament))

                prev_idx = i + 1

    return books


def get_book_text(books, testament):
    """ Get the text of a book in each testament """
    texts = {}

    for book, idcs in books.items(): 
        text_arr = testament[idcs[0] : idcs[1]]
        texts[book] =  " ".join(text_arr) 

    return texts


def delete_verse_identifiers(tokenized): 
    """ Find the bible verse identifiers and link them to their corresponding content """
    cleaned = []
    for sent in tokenized: 
        verse_id = re.match("[1-9][0-9]{0,2}:[1-9][0-9]{0,2}\.", sent)

        if not verse_id:
            cleaned.append(sent)

    return cleaned


def verse_tokenize(text, testament_title, book_id, book_title, verse_id):
    """ Tokenize the text into the given bible verses """
    verses = []

    indices = []
    values = []
    pattern = r"\b[1-9][0-9]{0,2}:[1-9][0-9]{0,2}\."

    for match in re.finditer(pattern, text):
        indices.append(match.start())
        values.append(match.group())

    for i, idx in enumerate(indices):
        verse = values[i]
        start = idx 
        end = len(text)-1 if i == len(indices)-1 else indices[i+1]

        verse_id_pos = re.search(pattern, text[start:end]) # remove bible verse identifier from the full text
        start = start + verse_id_pos.end()
        verse_text = text[start:end].strip()

        verses.append({"testament_title": testament_title, "book_id": book_id, "book_title": book_title, "verse_id": f"p_{verse_id}", "bible_verse": verse, "#chars": len(verse_text), "#words": len(word_tokenize(verse_text)), "text": verse_text})
        verse_id += 1

    return verses, verse_id


def sentence_tokenize(text, testament_title, book_id, book_title, sentence_id):
    """ Tokenize the text into sentences """
    sentences = [] 

    tokens = sent_tokenize(text) # has issues tokenize a handful of cases 
    cleaned_tokens = delete_verse_identifiers(tokens)

    for sent in cleaned_tokens:
        sentences.append({"testament_title": testament_title, "book_id": book_id, "book_title": book_title, "id": f"s_{sentence_id}", "#characters": len(sent), "#words": len(word_tokenize(sent)), "sentence": sent})
        sentence_id += 1

    return sentences, sentence_id


def write_testament(books, testaments, titles, tokenization="verses"): 
    """ Write the testament data and all its book to files """
    data = []
    sentence_id = 1
    verse_id = 1

    for num, testament in enumerate(testaments):
        texts = get_book_text(books[num], testament)
        testament_title = f"{titles[num]}_testament"

        for i, (book, text) in enumerate(texts.items()):
            file_name = f"../data/csv/bible_{tokenization}.csv"
            book_id = f"b_{len(books[num-1]) + i + 1}" if num != 0 else f"b_{i+1}"
            title_modified = book.lower().replace(" ", "_")

            # tokenize into sentences 
            if tokenization == "sentences":
                sentences, sentence_id = sentence_tokenize(text, testament_title, book_id, title_modified, sentence_id)
                data += sentences
            else: 
                verses, verse_id = verse_tokenize(text, testament_title, book_id, title_modified, verse_id)
                data += verses

    data = lexical_richness(data)
    data = lexical_novelty(data)

    df = pd.DataFrame(data=data)
    df.to_csv(file_name)


def lexical_richness(data): 
    """ Implementation of the TTR metric to measure lexical richness """
    for text_info in data: 
        tokens = word_tokenize(text_info["text"])
        types = set(tokens)

        text_info["TTR"] = len(types) / len(tokens)

    return data


def lexical_novelty(data): 
    """ Implementation of a simple metric for lexical novelty """
    novelty_threshold = 0.25
    decay_rate = 0.25

    novelty = 0 
    seen_words = []

    for text_info in data: 
        words = word_tokenize(text_info["text"])
        novel_words = 0
        for word in words: 
            if word not in seen_words: 
                novel_words += 1 
                seen_words.append(word)

        if novel_words / len(words) >= novelty_threshold: 
            novelty = 1
        else: 
            if novelty > 0: 
                novelty -= decay_rate

        text_info["novelty"] = novelty
    
    return data


def main():
    bible_url = "https://www.gutenberg.org/cache/epub/8300/pg8300.txt"
    out_name = "bible_project_gutenberg.txt"

    if not os.path.isfile(out_name):
        download_txt(bible_url, out_name)

    with open(out_name) as f:
        lines = f.readlines()
        old_toc, new_toc = get_contents(lines)
        old_testament, new_testament = split_testaments(lines)

        old_books = get_books(old_toc, old_testament)
        new_books = get_books(new_toc, new_testament)

        write_testament([old_books, new_books], [old_testament, new_testament], ["old", "new"], "verses")
        # write_testament([old_books, new_books], [old_testament, new_testament], ["old", "new"], "sentences")


if __name__ == "__main__":
    main()
