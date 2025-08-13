import sys

from get_book_info import (extract_isbn_fields,
                            out_sql_insert_to_file, print_book_info,
                            scrape_amazon_product_details)

PUBLISHER_ID = 14
FORMAT_ID = 4

def main():
    values = []
    if len(sys.argv) != 2:
        print("使い方: python main.py isbn_list.txt")
        sys.exit(1)

    filename = sys.argv[1]

    try:
        with open(filename, encoding="utf-8") as f:
            isbns = [line.strip() for line in f if line.strip()]
    except Exception as e:
        print(f"ファイルの読み込み中にエラーが発生しました: {e}")
        sys.exit(1)

    for isbn in isbns:
        url = f"https://www.amazon.co.jp/dp/{isbn}"

        print(f"\nISBN-10: {isbn} の書籍情報を取得しています...")
        print(f"URL: {url}")

        try:
            book_info = scrape_amazon_product_details(url)
            print_book_info(book_info)

            fields = extract_isbn_fields(book_info)
            sql = f"('{fields['title']}', {PUBLISHER_ID}, {fields['price']}, '{fields['isbn_13']}', '{fields['isbn_10']}', '{fields['sub_title']}', null, '{fields['release_date']}', {FORMAT_ID}, {fields['pages']}, '{fields['cover_image']}', CURRENT_TIMESTAMP)"
            values.append(sql)

        except Exception as e:
            print(f"ISBN {isbn} の情報取得中にエラー: {e}")

    out_sql_insert_to_file(values, "./SQL/INSERT_books.sql")

if __name__ == "__main__":
    main()