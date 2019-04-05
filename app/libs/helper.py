def is_isbn_or_key(word):
    """
        判断word是isbn还是关键字
        isbn13：13个0-9数字组成
        isbn10：10个0-9数字组成，含有一些'-'
    """
    isbn_or_key = 'key'
    if len(word) == 13 and word.isdigit():
        isbn_or_key = 'isbn'
    short_word = word.replace('-', '')
    if '-' in word and len(short_word) == 10 and short_word.isdigit():
        isbn_or_key = 'isbn'

    return isbn_or_key
