# 京都クエスト 本編拡張フェーズ HANDOFF

このリポジトリは、京都クエストMVP完成後の本編拡張用リポジトリです。
MVP途中の古い前提は `HANDOFF_MVP_ARCHIVE.md` に退避しています。

## 30秒サマリ

- MVPは完成済みです。
- 旧MVPリポジトリ `kyoto-quest-mvp` は保存済みです。
- 本編拡張リポジトリは `kyoto-quest` です。
- ローカル作業フォルダは `~/Projects/kyoto-quest` です。
- GitHub Pages入口は `index.html` です。
- 公開URLは `https://tomoyori0315.github.io/kyoto-quest/` です。
- `kyoto-quest.html` と `index.html` はコピー同期運用中です。片方を変えたら必ずもう片方へ同期してください。
- 通常URLでは仮想スティックが標準操作です。
- `?dpad=1` で旧固定D-padを表示できます。
- `?debug=1` でDBGボタンとデバッグ編集機能を有効化できます。

## 現在の完成状態

既存ステージは3つです。

- `sando`: 伏見稲荷 大鳥居前
- `romon`: 伏見稲荷 楼門・本殿前
- `senbon`: 伏見稲荷 千本鳥居

現行MVPで動いている主な機能は以下です。

- スマホ縦画面のCanvas 2D探索RPG
- 通常操作は左下タッチ開始の4方向仮想スティック
- `?dpad=1` で旧固定D-pad操作
- PCキーボード操作
- NPC会話
- 猫をなでる、猫帳登録、猫closeup表示、猫帳アイコン表示
- objectを調べる見聞カード
- 帳面の猫帳、見聞メモ、参拝記録
- sando / romon / senbon のステージ遷移
- 背景PNG、主人公/NPC/猫/UIの別レイヤー描画
- NPC / 猫の足元矩形ブロッカー
- iOS Safari / Chrome向けの長押しルーペ、選択、タップハイライト抑制
- `?debug=1` の隠しDBGモード
- DBGでのwalkable / blockers / entity radius / player collision確認と編集

## 操作モード

通常URL:

- 仮想スティック有効
- 固定D-pad非表示
- DBG非表示

`?dpad=1`:

- 旧固定D-pad表示
- 仮想スティック無効
- DBG非表示

`?debug=1`:

- 仮想スティック有効
- DBGボタン表示
- DBG ONで判定表示とデバッグ編集パネル表示

`?debug=1&dpad=1`:

- 旧固定D-pad表示
- DBGボタン表示

`?debug=0`:

- 同一ブラウザに保存されたdebug enabled状態を解除

## 現行データ管理

背景画像とは別に、歩ける範囲、ブロッカー、対象配置、出口をデータとして持ちます。

現行実装では、これらは `kyoto-quest.html` 内の `MAPS` オブジェクトと各 `*_ENTITIES` 配列で管理しています。

- `MAPS[sceneId].worldH`
- `MAPS[sceneId].spawn`
- `MAPS[sceneId].walkable`
- `MAPS[sceneId].blockers`
- `MAPS[sceneId].playerCollisionRadius`
- `MAPS[sceneId].entities`
- `SANDO_ENTITIES`
- `ROMON_ENTITIES`
- `SENBON_ENTITIES`

本編拡張フェーズ初期では、無理に外部JSON化しないでください。
ステージ数が増え、編集負荷が上がった時点で `data/maps/*.json` への分離を検討してよいです。

## 描画と当たり判定の注意

- 背景画像には主人公、NPC、猫、UI、会話ウィンドウ、DBG表示を描き込まないでください。
- 主人公、NPC、猫、UIは背景とは別レイヤーで描画します。
- `x, y` は基本的に足元アンカー、または反応判定中心として扱います。
- object / exit の反応は `entity.r` を使います。
- NPC / 猫の会話・なでる判定も `entity.r` を使います。
- NPC / 猫の物理衝突は `entity.r` ではなく、足元の小さい矩形hitboxで行います。
- 手動blockersは背景構造物用です。NPC / 猫まわりの補助blockerを安易に増やさないでください。
- 近接判定は「半径内で一番近い1つ」を拾うため、対象同士を近づけすぎないでください。

## 見聞カードと帳面

objectを調べると、短い見聞カードが表示されます。
カードは以下の要素を持ちます。

- タイトル
- ひとこと説明
- 本文
- 豆知識

調べたspotは `game.spots` に記録され、帳面の見聞メモに表示されます。
猫は `game.cats`、参拝記録は `game.visits` に記録されます。

## 次フェーズの拡張方針

今後は、本編ステージを以下の方向で追加していきます。

- JR稲荷駅前
- 奥社奉拝所・おもかる石
- 山道
- 四ツ辻
- 隠れ見晴らしステージ

追加時の基本手順:

1. 背景PNGを用意する
2. 背景には動くものを描き込まない
3. `MAPS` にscene定義を追加する
4. `*_ENTITIES` を追加する
5. walkable / blockers / entitiesをDBGで調整する
6. `kyoto-quest.html` と `index.html` を同期する
7. 通常URL、`?debug=1`、必要なら `?dpad=1` で確認する

## 変更時のルール

- ゲーム本体を変更する時は、既存の移動、仮想スティック、`?dpad=1`、`?debug=1`、NPC会話、猫なで、見聞カード、帳面、ステージ遷移、DBG機能を壊さないでください。
- `kyoto-quest.html` を変えたら、必ず `index.html` へ同じ内容を反映してください。
- ドキュメントだけの作業では、ゲーム本体に不要な差分を出さないでください。
- 確認時は `git diff --check` を通してください。
