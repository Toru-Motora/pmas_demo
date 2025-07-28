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
        "submit": {"type": "plain_text", "text": "実行"},
        "close": {"type": "plain_text", "text": "終了する"},
        "private_metadata": json.dumps(json_body),
        "blocks": [
            # {
            #     "block_id": "member_name",
            #     "type": "input",
            #     "element": {
            #         "type": "multi_users_select",
            #         "placeholder": {
            #             "type": "plain_text", 
            #             "text": " "
            #             },
            #         "initial_users": [member["id"] for member in member_details] if member_details and isinstance(member_details[0], dict) and "id" in member_details[0] else member_details,
            #         #"max_selected_items": 10,
            #     },
            #     "label": {
            #         "type": "plain_text", 
            #         "text": ":white_check_mark: プロジェクトメンバー"
            #     },
            #     "hint": {
            #         "type": "plain_text",
            #         "text": "チャンネルに参加しているユーザーが表示されています。\n入力内容をご確認頂き、MTG参加者を設定して下さい。",
            #     },
            # },
            {
                "block_id": "box_url",
                "type": "input",
                "element": {
                    "type": "plain_text_input",
                    "placeholder": {
                        "type": "plain_text",
                        "text": "https://sisco001.ent.box.com/file/xxxxxxxxxx",
                    },
                    "action_id": "box_file_path",
                },
                "label": {
                    "type": "plain_text", 
                    "text": "Boxリンク"
                },
                "hint": {
                    "type": "plain_text",
                    "text": "打ち合わせの録音ファイル（m4a形式）をBoxで表示し、ブラウザで表示されたURLを貼り付けてください。",
                },
            },
            {
                "block_id": "agenda",
                "type": "input",
                "optional": True, # True = 任意
                "element": {
                    "type": "plain_text_input",
                    "multiline": True,
                    "placeholder": {
                        "type": "plain_text",
                        "text": "変更管理の追加費用について合意する\n6月中に検収する方針で合意する\nUIの仕様を確定する",
                    },
                },
                "label": {
                    "type": "plain_text", 
                    "text": "個別評価項目"
                    },
                "hint": {
                    "type": "plain_text",
                    "text": "基本分析に加えて、ここに入力された項目をPMアシスタントが個別に評価します。確認したい観点を1行に1つずつ入力してください。",
                },
            },
        ],
    }
