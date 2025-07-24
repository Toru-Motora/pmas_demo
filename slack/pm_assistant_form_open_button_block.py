def pm_assistant_form_open_button_block():
    """
    PMアシスタントAI分析に必要なの入力フォームを呼び出すボタン付きテキストブロックを作成します。
    """
    return [
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "ボタンを押してPMアシスタントAIを実行します。",
            },
        },
        {
            "type": "actions",
            "elements": [
                {
                    "type": "button",
                    "style": "primary",
                    "text": {"type": "plain_text", "text": "PMアシスタントAI"},
                    "action_id": "pma-form-open-submit-button",
                }
            ],
        },
        {
            "type": "context",
            "elements": [
                {
                    "type": "mrkdwn",
                    "text": "PMアシスタントAIは、MTGアウトラインとの乖離があるか判断します。\n打合せ後に実行し、アシスタントAIの結果を基に打合せの振り返り会を実施して下さい。\nプロジェクトの潜在的なリスクを早期に発見し、炎上の芽を摘み取ることができます。",
                }
            ],
        },
    ]
