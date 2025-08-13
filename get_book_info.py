import re

import requests
from bs4 import BeautifulSoup


def scrape_amazon_product_details(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"URLへのアクセス中にエラーが発生しました: {e}")
        return None

    soup = BeautifulSoup(response.text, "html.parser")

    product_details = {}

    # タイトル
    title_element = soup.find("span", id="productTitle")
    main_title = ""
    if title_element:
        main_title = title_element.get_text(strip=True)
        product_details["タイトル"] = main_title

    # --- サブタイトル取得の改善 (再々調整) ---
    subtitle = None
    # 1. id="productSubtitle" の要素を探す（これが最優先）
    subtitle_element = soup.find("span", id="productSubtitle")
    if subtitle_element:
        subtitle = subtitle_element.get_text(strip=True)
    else:
        # 2. タイトルからフォーマット情報（例: (文庫 - YYYY/MM/DD)）を除外
        # このパターンをサブタイトルと誤認しないようにする
        format_date_pattern = re.compile(r"\s*\([^)]*?[-—]\s*\d{4}/\d{1,2}/\d{1,2}\)")
        cleaned_title = format_date_pattern.sub("", main_title).strip()

        # 3. クリーニング後のタイトルからサブタイトルを推測する
        # 全角コロン、半角コロン、ダッシュ、全角ダッシュなどで分割を試みる
        potential_delimiters = ["：", ":", "—", " - "]
        temp_title = cleaned_title  # 分割試行用のタイトル

        for delimiter in potential_delimiters:
            if delimiter in temp_title:
                parts = temp_title.split(
                    delimiter, 1
                )  # 最初に見つかった区切り文字で一度だけ分割
                if len(parts) > 1:
                    potential_subtitle_part = parts[1].strip()
                    # サブタイトルが短すぎる、または特定できない文字だけの場合は採用しない
                    if len(potential_subtitle_part) > 5 and not re.fullmatch(
                        r"[^\w\s]*", potential_subtitle_part
                    ):
                        product_details["タイトル"] = parts[
                            0
                        ].strip()  # タイトルをサブタイトルなしに更新
                        subtitle = potential_subtitle_part
                        break  # 見つかったらループを抜ける

        # ここで最終的なタイトルを確定 (サブタイトル分割が行われなかった場合はcleaned_title)
        if (
            "タイトル" not in product_details
        ):  # 上の推測でタイトルが更新されていなければ
            product_details["タイトル"] = cleaned_title

    product_details["サブタイトル"] = (
        subtitle if subtitle else "N/A"
    )  # 取得できなければN/A

    # 著者
    author_elements = soup.find_all(
        "a", class_="a-link-normal", attrs={"data-hook": "product-link"}
    )
    authors = [author.get_text(strip=True) for author in author_elements]
    if authors:
        product_details["著者"] = ", ".join(authors)
    else:
        author_text_element = soup.find("div", id="bylineInfo")
        if author_text_element:
            author_names = re.findall(
                r"([^,]+?)\s+\(著", author_text_element.get_text()
            )
            if author_names:
                product_details["著者"] = ", ".join(
                    [name.strip() for name in author_names]
                )
            else:
                first_author_text = author_text_element.get_text(strip=True).split(
                    " (著"
                )[0]
                if first_author_text:
                    product_details["著者"] = first_author_text.strip()

    # 価格
    price_whole_element = soup.find("span", class_="a-price-whole")
    price_symbol_element = soup.find("span", class_="a-price-symbol")

    if price_whole_element and price_symbol_element:
        price_symbol = price_symbol_element.get_text(strip=True)
        price_whole = price_whole_element.get_text(strip=True)
        product_details["価格"] = f"{price_symbol}{price_whole}"
    else:
        offscreen_price_element = soup.find("span", class_="aok-offscreen")
        if offscreen_price_element:
            clean_price = (
                offscreen_price_element.get_text(strip=True)
                .replace("\n", "")
                .replace("\u200b", "")
                .strip()
            )
            if clean_price and clean_price.startswith("￥"):
                product_details["価格"] = clean_price

    # 出版社、発売日、ISBN、ページ数
    detail_bullets_div = soup.find("div", id="detailBullets_feature_div")
    if detail_bullets_div:
        list_items = detail_bullets_div.find_all("li")
        previous_item_text = None

        for item_index, item in enumerate(list_items):
            current_item_text_full = (
                item.get_text(strip=True)
                .replace("\u200f", "")
                .replace("\u200b", "")
                .replace("\n", "")
                .strip()
            )

            text_bold = item.find("span", class_="a-text-bold")
            if text_bold:
                key = (
                    text_bold.get_text(strip=True)
                    .replace(":", "")
                    .replace(" ", "")
                    .replace("\u200f", "")
                    .replace("\u200b", "")
                    .strip()
                )

                value_span = text_bold.find_next_sibling("span")
                clean_value = ""
                if value_span:
                    clean_value = (
                        value_span.get_text(strip=True)
                        .replace("\u200f", "")
                        .replace("\u200b", "")
                        .replace("\n", "")
                        .strip()
                    )

                if "出版社" in key:
                    match = re.search(r"(.+?)\s*\((.+?)\)", clean_value)
                    if match:
                        product_details["出版社"] = match.group(1).strip()
                        product_details["発売日"] = match.group(2).strip()
                    else:
                        product_details["出版社"] = clean_value
                elif "発売日" in key:
                    if "発売日" not in product_details:
                        product_details["発売日"] = clean_value
                elif "ISBN-10" in key:
                    product_details["ISBN-10"] = clean_value
                    if item_index > 0 and "ページ数" not in product_details:
                        page_match = re.search(r"(\d+)\s*ページ", previous_item_text)
                        if page_match:
                            product_details["ページ数"] = page_match.group(1) + "ページ"
                elif "ISBN-13" in key:
                    product_details["ISBN-13"] = clean_value

            previous_item_text = current_item_text_full

    # ページ数 (rpi-attribute-valueからの取得も引き続き試みる - 予備)
    if "ページ数" not in product_details:
        page_span_elements = soup.find_all("span", class_="rpi-attribute-value")
        for p_span in page_span_elements:
            page_text = p_span.get_text(strip=True)
            page_match = re.search(r"(\d+)\s*ページ", page_text)
            if page_match:
                product_details["ページ数"] = page_match.group(1) + "ページ"
                break

    return product_details


def print_book_info(book_info):
    if book_info:
        print("\n--- 取得結果 ---")
        print(f"タイトル: {book_info.get('タイトル', 'N/A')}")
        print(f"サブタイトル: {book_info.get('サブタイトル', 'N/A')}")
        print(f"著者: {book_info.get('著者', 'N/A')}")
        print(f"出版社: {book_info.get('出版社', 'N/A')}")
        print(f"発売日: {book_info.get('発売日', 'N/A')}")
        print(f"ページ数: {book_info.get('ページ数', 'N/A')}")
        print(f"ISBN-10: {book_info.get('ISBN-10', 'N/A')}")
        print(f"ISBN-13: {book_info.get('ISBN-13', 'N/A')}")
        print(f"価格: {book_info.get('価格', 'N/A')}")
    else:
        print(
            "商品の詳細を抽出できませんでした。URLが正しいか、またはウェブサイトの構造が変更されていないか確認してください。"
        )


def extract_isbn_fields(book_info):
    """必要なSQL用フィールドを整形"""
    return {
        "title": sanitize(book_info.get("タイトル", "")),
        "sub_title": sanitize(book_info.get("サブタイトル", "").split("–")[0].strip()),
        "price": int(
            book_info.get("価格", "￥0").replace("￥", "").replace(",", "").strip() or 0
        ),
        "isbn_13": book_info.get("ISBN-13", "").replace("-", ""),
        "isbn_10": book_info.get("ISBN-10", ""),
        "release_date": book_info.get("発売日", "").replace("/", "-"),
        "pages": int(
            book_info.get("ページ数", "0ページ").replace("ページ", "").strip() or 0
        ),
        "cover_image": book_info.get("ISBN-13", "").replace("-", "") + ".jpg",
    }


def sanitize(s: str) -> str:
    """SQL用にシングルクオートなどをエスケープ"""
    return s.replace("'", "''")


def out_sql_insert(values):
    """SQL INSERT文を出力"""
    if values:
        print("\n--- SQL INSERT 文 ---\n")
        print(
            "INSERT INTO public.books(title, publisher_id, price, isbn, isbn_10, sub_title, edition, release_date, format_id, pages, book_cover_image_name, created_at)"
        )
        print("VALUES")
        print("    " + ",\n    ".join(values) + ";")


def out_sql_insert_to_file(values, filename="output.sql"):
    """SQL INSERT文をファイルに出力"""
    if values:
        try:
            with open(filename, "w", encoding="utf-8") as f:
                f.write(
                    "INSERT INTO public.books(title, publisher_id, price, isbn, isbn_10, sub_title, edition, release_date, format_id, pages, book_cover_image_name, created_at)\n"
                )
                f.write("VALUES\n")
                f.write("    " + ",\n    ".join(values) + ";\n")
            print(f"\n✅ SQL文を {filename} に出力しました。")
        except Exception as e:
            print(f"SQLファイル書き込み時にエラー: {e}")
