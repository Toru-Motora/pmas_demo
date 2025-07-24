import json
from datetime import date
from os import getenv

_enclosed_one_code = int.from_bytes("①".encode("UTF-8"), "big")


def number_to_enclosed_numeric(oneBasedNumber: int) -> str:
    """1以上20以下の数字を丸付き文字に変換します。"""
    enclosed_numeric_code = _enclosed_one_code + oneBasedNumber - 1
    return enclosed_numeric_code.to_bytes(4, "big").decode("UTF-8")


# _purpose_options = tuple(
#     map(
#         lambda v: {
#             "text": {
#                 "type": "plain_text",
#                 "text": number_to_enclosed_numeric(v[0]) + v[1][0],
#             },
#             "value": str(v[1][1]),
#         },
#         enumerate(
#             json.loads(getenv("PURPOSE_OPTIONS")).items(),
#             1,
#         ),
#     )
# )


def pma_form_block(slack_user_id: str):
    """
    PMアシスタントの入力フォームのブロックを作成します。
    """
    today = f"{date.today():%Y-%m-%d}"

    return {
        "type": "modal",
        "callback_id": "pma_form",
        "title": {"type": "plain_text", "text": "炎上リスクをチェック"},
        "submit": {"type": "plain_text", "text": "チェック"},
        "close": {"type": "plain_text", "text": "閉じる"},
        "blocks": [
            {
                "block_id": "project_name",
                "type": "input",
                "element": {
                    "type": "plain_text_input",
                    "placeholder": {
                        "type": "plain_text",
                        "text": "プロジェクト名を入力してください",
                    },
                },
                "label": {
                    "type": "plain_text", 
                    "text": ":white_check_mark: プロジェクト名"
                    },
                "hint": {
                    "type": "plain_text",
                    "text": "例.生成AIチャットボット案件 B銀行様など",
                },
            },
            {
                "block_id": "manager_name",
                "type": "input",
                "element": {
                    "type": "multi_users_select",
                    "placeholder": {
                        "type": "plain_text", 
                        "text": "例.課長などラインマネージャー"
                        },
                    #"max_selected_items": 10,
                },
                "label": {
                    "type": "plain_text", 
                    "text": ":white_check_mark: プロジェクト責任者"
                    },
                "hint": {
                    "type": "plain_text",
                    "text": "炎上リスクがあった場合にアラートを通知します。炎上リスクの早期発見・報告は炎上防止の為に重要な観点です。",
                },
            },
            {
                "block_id": "member_name",
                "type": "input",
                "element": {
                    "type": "multi_users_select",
                    "placeholder": {
                        "type": "plain_text", 
                        "text": "プロジェクトメンバーを追加してください"
                        },
                    "initial_users": [slack_user_id],
                    #"max_selected_items": 10,
                },
                "label": {
                    "type": "plain_text", 
                    "text": ":white_check_mark: プロジェクトメンバー"
                    },
            },
            {
                "block_id": "agenda",
                "type": "input",
                "element": {
                    "type": "plain_text_input",
                    "multiline": True
                    "placeholder": {
                        "type": "plain_text",
                        "text": "MTGアウトライン（当初の計画）を入力してください",
                    },
                },
                "label": {
                    "type": "plain_text", 
                    "text": ":white_check_mark: MTGアウトライン"
                    },
                "hint": {
                    "type": "plain_text",
                    "text": "例.\n1. Fit&Gapでの検討事項の共有\n2. ヒアリングシートの確認\n3. デモ環境の説明など",
                },
            },
            {
                "block_id": "box_url",
                "type": "input",
                "element": {
                    "type": "plain_text_input",
                    "placeholder": {
                        "type": "plain_text",
                        "text": "Box上の録画/音声ファイルの共有リンク(URL)を入力",
                    },
                    "action_id": "box_file_path",
                },
                "label": {
                    "type": "plain_text", 
                    "text": ":white_check_mark:打合せの音声/録画ファイル"
                },
                "hint": {
                    "type": "plain_text",
                    "text": "例: https://sisco001.ent.box.com/file/ファイル名.mp4\n※ローカルパス (C:/Users/...) は使用できません。",
                },
            },
            # {
            #     "block_id": "image_file",
            #     "type": "input",
            #     "element": {
            #         "type": "file_input",
            #         "max_files": 1,
            #         "filetypes": ["jpg", "png"],
            #     },
            #     "label": {"type": "plain_text", "text": "画像アップロード"},
            #     "hint": {
            #         "type": "plain_text",
            #         "text": "出席者全員がわかる、食事中の画像を添付してください。店内撮影不可の場合は店舗前や看板前の画像でも可能です。",
            #     },
            #     "optional": optional_upload_image,
            # },
            # {
            #     "block_id": "other_participants",
            #     "type": "input",
            #     "element": {
            #         "type": "plain_text_input",
            #         "placeholder": {
            #             "type": "plain_text",
            #             "text": "その他の参加者を入力",
            #         },
            #     },
            #     "label": {"type": "plain_text", "text": "その他の参加者"},
            #     "hint": {
            #         "type": "plain_text",
            #         "text": "「参加者」で選択できなかった方について、お名前を入力してください。複数人の場合、「セゾン太郎,セゾン花子」のようにカンマで区切ってください。",
            #     },
            #     "optional": True,
            # },
            # {"type": "divider"},
            # {
            #     "type": "section",
            #     "text": {
            #         "type": "mrkdwn",
            #         "text": "\n".join(
            #             [
            #                 "*投稿時のSlackbotからの通知について*",
            #                 "投稿するとSlackbotから、「<アプリ名> さんがあなたのプライベートファイル <画像ファイル名> を #movランチ さんと共有しました。」という通知が送信されます。",
            #                 "アプリからファイル共有した場合のSlackの仕様によるもので、問題はございません。",
            #             ]
            #         ),
            #     },
            # },
        ],
    } 