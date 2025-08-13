import sys

from libs.get_book_info import (
    extract_isbn_fields,
    out_sql_insert_to_file,
    print_book_info,
    fetch_google_books_info,
    scrape_amazon_product_details,
)

PUBLISHER_ID = 14
FORMAT_ID = 4

def main():
    values = []
    # コマンドライン引数: isbn_list.txt [--google|--amazon]
    if len(sys.argv) < 2 or len(sys.argv) > 3:
        print("使い方: python main.py isbn_list.txt [--google|--amazon]")
        sys.exit(1)

    filename = sys.argv[1]
    mode = "amazon"  # デフォルト
    if len(sys.argv) == 3:
        if sys.argv[2] == "--amazon":
            mode = "amazon"
        elif sys.argv[2] == "--google":
            mode = "google"
        else:
            print("第2引数は --google または --amazon を指定してください")
            sys.exit(1)

    try:
        with open(filename, encoding="utf-8") as f:
            isbns = [line.strip() for line in f if line.strip()]
    except Exception as e:
        print(f"ファイルの読み込み中にエラーが発生しました: {e}")
        sys.exit(1)

    for isbn in isbns:
        if mode == "google":
            print(f"\nISBN: {isbn} の書籍情報をGoogle Books APIから取得しています...")
            try:
                book_info = fetch_google_books_info(isbn)
                print_book_info(book_info)
                fields = extract_isbn_fields(book_info)
                sql = f"('{fields['title']}', {PUBLISHER_ID}, {fields['price']}, '{fields['isbn_13']}', '{fields['isbn_10']}', '{fields['sub_title']}', null, '{fields['release_date']}', {FORMAT_ID}, {fields['pages']}, '{fields['cover_image']}', CURRENT_TIMESTAMP)"
                values.append(sql)
            except Exception as e:
                print(f"ISBN {isbn} の情報取得中にエラー: {e}")
        else:
            print(f"\nISBN: {isbn} の書籍情報をAmazonから取得しています...")
            try:
                book_info = scrape_amazon_product_details(isbn)
                print_book_info(book_info)
                fields = extract_isbn_fields(book_info)
                sql = f"('{fields['title']}', {PUBLISHER_ID}, {fields['price']}, '{fields['isbn_13']}', '{fields['isbn_10']}', '{fields['sub_title']}', null, '{fields['release_date']}', {FORMAT_ID}, {fields['pages']}, '{fields['cover_image']}', CURRENT_TIMESTAMP)"
                values.append(sql)
            except Exception as e:
                print(f"ISBN {isbn} の情報取得中にエラー: {e}")

    out_sql_insert_to_file(values, "./SQL/INSERT_books.sql")

if __name__ == "__main__":
    main()