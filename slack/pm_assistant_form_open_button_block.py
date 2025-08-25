def pm_assistant_form_open_button_block():
    """
    PMアシスタントAI分析に必要な入力フォームを呼び出すボタン付きテキストブロックを作成します。
    """
    return [
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "プロジェクトのリスク評価を行います",
            },
        },
        {
            "type": "actions",
            "elements": [
                {
                    "type": "button",
                    "style": "primary",
                    "text": {"type": "plain_text", "text": "開始する"},
                    "action_id": "pma-form-open-submit-button",
                }
            ],
        },
        {
            "type": "context",
            "elements": [
                {
                    "type": "mrkdwn",
                    "text": "お客様との打合せ録音データを分析してリスク評価を行います。\n打合せ後に必ずリスク評価をしてください。評価を確認してリスクをケアしてください。\nリスク評価にかかる時間は、1時間の打ち合わせで10分前後です。",
                }
            ],
        },
    ]
