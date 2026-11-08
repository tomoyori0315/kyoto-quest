# 京都クエスト

京都・伏見稲荷を舞台にした、スマホ縦画面の探索型Web RPGです。
HTML・CSS・JavaScriptとPNG素材で動作し、ゲームのビルドは不要です。
開発ルールは `AGENTS.md`、実装状況と操作方法は `HANDOFF.md` を参照してください。

## 起動

リポジトリ直下で次を実行し、`http://127.0.0.1:8000/` を開きます。

```sh
python3 -m http.server 8000 --bind 127.0.0.1
```

終了は `Ctrl+C` です。公開入口は `index.html` です。
`kyoto-quest.html` を編集したら、必ず `index.html` に同じ内容を反映します。

## 変更後のチェック

検査にはPython 3とNode.jsを使用します。追加パッケージのインストールは不要です。
Node.jsはJavaScriptの構文検査にだけ使用し、ゲームを遊ぶ際には不要です。

```sh
python3 scripts/check_project.py
```

以下を検査し、すべて通れば終了コード0、問題があれば1を返します。

- `kyoto-quest.html` と `index.html` のバイト単位の一致
- 本体HTML内に文字列として書かれた `assets/...png` 参照のファイル存在
- インラインJavaScriptの構文（`node --check`）
- HTML2本、通常・DBG・D-padのURL、参照PNGのHTTP 200応答と配信内容の一致

HTTP検査では、この作業環境のループバックアドレスで空きポートを使用し、
終了時にサーバーを停止します。外部サービスへの通信や公開は行いません。
Node.jsが見つからない場合や、サーバーを起動できない場合も検査失敗になります。

この検査はブラウザでJavaScriptを実行しません。動的に組み立てる画像パス、
移動・会話・猫帳・ステージ遷移・描画・iPhoneのタッチ操作は別途確認が必要です。
通常・DBG・D-padのURL検査も、各操作モードの動作を保証するものではありません。
変更時は併せて `git diff --check` を実行してください。

## PRの自動チェック（Step AUTO-05）

`main` 向けPRの作成・更新・再オープン時（Draftを含む）と、`main` へのpush時に、
GitHub Actionsの `Project checks` が同じ検証コマンドを実行します。
実行環境はUbuntu 24.04、Python 3.12、Node.js 24です。
追加パッケージ、APIキー、Secretsの登録は不要です。

PRの「Checks」で `Static game checks` を開き、成功・失敗と検査ログを確認してください。
失敗時はログの `FAIL` を確認して修正し、同じPRへpushすると再検査されます。
同じPRで新しい検査が始まると、実行途中の古い検査は取り消されます。

このワークフローは検査のみで、自動マージやゲームの公開は行いません。
チェック失敗時のマージ禁止は、別途ブランチ保護の設定が必要です。
既存のGitHub Pagesは引き続き `main` の更新で公開されるため、
この検査の成功を待ってから本人承認でマージしてください。
