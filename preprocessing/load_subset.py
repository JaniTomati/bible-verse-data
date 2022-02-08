#!/usr/bin/env python3


import pandas as pd 


def main():
  bible_csv = "bible_verses.csv"
  out_name = "test_subset.csv"

  column = "book_title"
  books = ["the_book_of_genesis", "the_holy_gospel_of_jesus_christ_according_to_saint_matthew"]

  df = pd.read_csv(bible_csv)
  df_sub = df[(df[column] == books[0]) | (df[column] == books[1])]
  df_sub.to_csv(out_name)


if __name__ == "__main__":
    main()