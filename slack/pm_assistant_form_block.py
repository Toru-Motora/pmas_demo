import json
from datetime import date
from os import getenv


def pm_assistant_form_block(slack_user_id: str, member_details: list[str], json_body: dict):
    """
    # PMアシスタントの入力フォームのブロックを作成します
    # この関数はSlackモーダル用のフォームブロックを返します
    # member_details: プロジェクトメンバー情報のリスト（任意）
    # slack_user_id: フォームを開いたユーザーのSlack ID
    # json_body: モーダルのprivate_metadataに格納する情報
    """

    return {
        "type": "modal",
        "callback_id": "pm_assistant_form",
        "title": {"type": "plain_text", "text": "プロジェクトリスク評価"},
        "submit": {"type": "plain_text", "text": "分析"},
        "close": {"type": "plain_text", "text": "終了する"},
        "private_metadata": json.dumps(json_body),
        "blocks": [
            {
                "block_id": "box_url",
                "type": "input",
                "element": {
                    "type": "plain_text_input",
                    "placeholder": {
                        "type": "plain_text",
                        "text": "例）https://sisco001.ent.box.com/file/xxxxxxxxxx",
                    },
                    "action_id": "box_file_path",
                },
                "label": {
                    "type": "plain_text", 
                    "text": "Box URL（録音ファイル）"
                },
                "hint": {
                    "type": "plain_text",
                    "text": "会議の録音ファイル（m4a、mp4形式）のURLを貼り付けてください。",
                },
            },
            {
                "block_id": "box_outline_url",
                "type": "input",
                "optional": True, # True = 任意
                "element": {
                    "type": "plain_text_input",
                    "placeholder": {
                        "type": "plain_text",
                        "text": "例）https://sisco001.ent.box.com/file/xxxxxxxxxx",
                    },
                    "action_id": "box_outline_file_path",
                },
                "label": {
                    "type": "plain_text", 
                    "text": "Box URL（ミーティングアウトライン）"
                },
                "hint": {
                    "type": "plain_text",
                    "text": "ミーティングアウトライン（xlsx形式）のURLを張り付けてください。",
                },
            },
            {
                "block_id": "box_outline_no",
                "type": "input",
                "optional": True, # True = 任意
                "element": {
                    "type": "plain_text_input",
                    "placeholder": {
                        "type": "plain_text",
                        "text": "例）1～9999の整数",
                    },
                    "action_id": "box_outline_no",
                },
                "label": {
                    "type": "plain_text", 
                    "text": "ミーティングアウトライン番号"
                },
                "hint": {
                    "type": "plain_text",
                    "text": "※ Box URL（ミーティングアウトライン）を利用する際は、ミーティングアウトライン番号を必ず入力してください。",
                },
            },
            # {
            #     "block_id": "outline_box_url",
            #     "type": "input",
            #     "element": {
            #         "type": "plain_text_input",
            #         "placeholder": {
            #             "type": "plain_text",
            #             "text": "例）https://sisco001.ent.box.com/file/xxxxxxxxxx",
            #         },
            #         "action_id": "outline_box_file_path",
            #     },
            #     "label": {
            #         "type": "plain_text", 
            #         "text": "ミーティングアウトラインのBoxURL"
            #     },
            #     "hint": {
            #         "type": "plain_text",
            #         "text": "ミーティングアウトラインファイル（xlsx形式）をBoxで表示し、ブラウザで表示されたURLを貼り付けてください。",
            #     },
            # },
            # {
            #     "block_id": "agenda",
            #     "type": "input",
            #     # "optional": True, # True = 任意
            #     "element": {
            #         "type": "plain_text_input",
            #         "multiline": True,
            #         "placeholder": {
            #             "type": "plain_text",
            #             "text": "例）\n・変更管理の追加費用について合意する（期限：8/1）\n・6月中に検収する方針で合意する（期限：8/1）\n・UIの仕様を確定する（期限：8/1）",
            #         },
            #     },
            #     "label": {
            #         "type": "plain_text", 
            #         "text": "ミーティングアウトラインの項目"
            #         },
            #     "hint": {
            #         "type": "plain_text",
            #         "text": "入力されたミーティングアウトラインの項目をPMアシスタントが個別に評価します。確認観点を1行に1つずつ入力してください。",
            #     },
            # },
        ],
    }
