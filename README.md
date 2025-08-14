## 仮想環境を作成(最初だけ)
```
uv venv
```

## 仮想環境へ入る
```
source .venv/bin/activate
(book) taketomooishi@TAKETOMOnoMacBook-Air book %
```

## 仮想環境内にpyproject.tomlに書かれている依存関係全てを適用
```
uv sync
```

## 実行
```
python main.py isbn_list.txt
python main.py isbn_list.txt --google
python main.py isbn_list.txt --amazon
```

以上