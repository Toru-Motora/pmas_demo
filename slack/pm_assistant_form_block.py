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
        "title": {"type": "plain_text", "text": "炎上リスクをチェック"},
        "submit": {"type": "plain_text", "text": "チェック"},
        "close": {"type": "plain_text", "text": "閉じる"},
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
                        "text": "Box上の録画/音声ファイルの共有リンク(URL)を入力",
                    },
                    "action_id": "box_file_path",
                },
                "label": {
                    "type": "plain_text", 
                    "text": ":white_check_mark:打合せの音声/録画ファイル(m4a/mp4形式)"
                },
                # "hint": {
                #     "type": "plain_text",
                #     "text": "例: https://sisco001.ent.box.com/file/s/xxxxxxxxxx\n※ローカルパス (C:/Users/...) は使用できません。",
                # },
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
                        "text": "例.\n1. 変更管理の追加費用について合意する\n2. 6月中に検収する方針で合意する\n3. UIの仕様を確定させる",
                    },
                },
                "label": {
                    "type": "plain_text", 
                    "text": ":white_check_mark: 個別分析エリア"
                    },
                "hint": {
                    "type": "plain_text",
                    "text": "個別に状況分析を行います。打合せで実施予定の事柄がある場合は1行単位で入力してください。",
                },
            },
        ],
    }
