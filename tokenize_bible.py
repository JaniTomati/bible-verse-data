#!/usr/bin/env python3

import re
import os
import shutil
import urllib.request
import pandas as pd 

from nltk.tokenize import sent_tokenize


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


def delete_psalm_identifiers(tokenized): 
    """ Find the psalm identifiers and link them to their corresponding content """
    cleaned = []
    for sent in tokenized: 
        psalm_id = re.match("[1-9][0-9]{0,2}:[1-9][0-9]{0,2}\.", sent)

        if not psalm_id:
            cleaned.append(sent)

    return cleaned


def psalm_tokenize(text):
    """ Tokenize the text into the given psalms """
    psalms = []

    indices = []
    values = []

    for match in re.finditer("[1-9][0-9]{0,2}:[1-9][0-9]{0,2}\.", text):
        indices.append(match.start())
        values.append(match.group())

    for i, idx in enumerate(indices):
        psalm = values[i]
        start = idx 
        end = len(text)-1 if i == len(indices)-1 else indices[i+1]

        psalm_id_pos = re.search("[1-9][0-9]{0,2}:[1-9][0-9]{0,2}\.", text[start:end]) # remove psalm identifier from the full text
        start = start + psalm_id_pos.end()

        psalms.append({"psalm": psalm, "length": len(text[start:end]), "text": text[start:end]})

    return psalms


def write_testament(books, testament, testament_id): 
    """ Write the testament data and all its book to files """
    global sentence_id
    tokenization = "psalms" # else psalms 

    texts = get_book_text(books, testament)
    folder = "old_testament" if testament_id == "old" else "new_testament"

    for book, text in texts.items():
        title_modified = book.lower().replace(" ", "_")
        file_name = f"{title_modified}.csv"

        # tokenize into sentences 
        if tokenization == "sentences":
            tokens = sent_tokenize(text) # has issues tokenize a handful of cases 
            cleaned_tokens = delete_psalm_identifiers(tokens)

            data = []
            for sent in cleaned_tokens:
                data.append({"id": sentence_id, "length": len(sent), "sentence": sent})
                sentence_id += 1
        else: 
            data = psalm_tokenize(text) 

        df = pd.DataFrame(data=data)
        df.to_csv(f"{folder}/{file_name}")
        print(f"{folder}/{file_name}")


def get_key_words():
    pass 


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

        write_testament(old_books, old_testament, "old")
        write_testament(new_books, new_testament, "new")


if __name__ == "__main__":
    main()
