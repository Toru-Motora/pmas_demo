import os
import logging
import json
from sys import addaudithook
from flask import Flask, jsonify
from threading import Thread
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from slack.pm_assistant_form_open_button_block import pm_assistant_form_open_button_block
from slack.pm_assistant_form_block import pm_assistant_form_block
from logging import Logger
import requests
from lib.getsasurl import get_container_sas_url

# ロガーを設定（これにより、Boltの内部ログも表示されやすくなります）
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Constants should have UPPER_CASE names
# CACHE_USE_FLAG = "DUMMY"
AI_SERVICE = "AOAI"
AI_MODEL = "gpt-4o"
AI_TEMPERATURE = 0
# BOT_TOKEN = "XXXXX"

# 環境変数からトークンを読み込む
# アプリのインストールに成功すると 2 つのトークンが生成される。
# SLACK_BOT_TOKEN: xoxb- から始まる Bot User OAuth Token
# SLACK_APP_TOKEN: xapp- から始まる App-Level Token (ソケットモード用 / Basic Information)
bot_token = os.environ.get("SLACK_BOT_TOKEN")
app_token = os.environ.get("SLACK_APP_TOKEN")

# トークンが正しく読み込まれたかを確認するためのログ
if not bot_token:
    logger.error("SLACK_BOT_TOKEN が設定されていません。")
if not app_token:
    logger.error("SLACK_APP_TOKEN が設定されていません。")

# Flaskアプリの初期化
flask_app = Flask(__name__)

@flask_app.route("/")
def home():
    return jsonify({
        "status": "running",
        "app": "PMアシスタント",
        "description": "PMアシスタントアプリが実行中です"
    })

@flask_app.route("/health")
def health():
    return jsonify({"status": "healthy"})

# ボットトークンとソケットモードハンドラーを使ってアプリを初期化します
app = App(token=bot_token)


def get_access_token():
    """
    login API.を使ってHULFT Square認証情報からアクセストークンを取得
    """
    url = 'https://app.square.hulft.com/v1/users/login'
    body = {
        # "email": "himeka_kawaguchi+pma@saison-technology.com",
        "email": "toru_motora@saison-technology.com",
        "password": os.environ.get("HSQ_SIGNING_SECRET")
    }
    headers = {
        'Content-Type': 'application/json'
    }
    try:
        response = requests.post(url, json=body, headers=headers, verify=False)
        response.raise_for_status()
        data = response.json()
        return data['accessToken'], data['challenge']
    except requests.exceptions.RequestException as e:
        raise

def update_refresh_token(access_token):
    """アクセストークンを使いリフレッシュトークンを更新"""
    url = 'https://app.square.hulft.com/v1/rest-api-token'
    body = {
        "refreshToken": os.environ.get("HSQ_REFRESH_TOKEN") 
    }
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {access_token}'
    }
    try:
        response = requests.post(url, json=body, headers=headers, verify=False)
        response.raise_for_status()
        data = response.json()
        return data['accessToken']
    except requests.exceptions.RequestException as e:
        raise

# HULFT Squareジョブ
# def invoke_hsq_llm_api(channel, thread_ts, slack_user_id, cache_use_flag,
#                        ai_service, ai_model, ai_temperature, bot_token):
#def invoke_hsq_llm_api(access_token,channel):
def invoke_hsq_llm_api(access_token,channelId):
    """HULFT Squareジョブを実行"""
    url = 'https://a00001-21.square.hulft.com/PMAssistant/pmademo'
    body = {
        # 'prompt': prompt,
        'channelId': channelId
        # 'thread_ts': thread_ts,
        # 'slack_user_id': slack_user_id,
        # 'cache_use_flag': cache_use_flag,
        # 'ai_service': ai_service,
        # 'ai_model': ai_model,
        # 'ai_temperature': ai_temperature,
        # 'bot_token': bot_token
    }
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {access_token}',
        'X-HSQ-Async': 'true'
    }
    try:
        response = requests.post(url, json=body, headers=headers)
        response.raise_for_status()
        return response
    except requests.exceptions.RequestException as e:
        raise 

# # Slack API実行用メソッド
# def _get_user_profile_by_slack_user_id(client, user_id: str):
#     """SlackのユーザーIDからユーザー情報を取得します。"""
#     if not user_id:
#         return None

#     user_info = client.users_info(user=user_id)
#     return user_info["user"]["profile"]

# @app.message("こんにちは")
# def message_hello(message, say):
#     # イベントがトリガーされたチャンネルへ say() でメッセージを送信します
#     say(f"PMアシスタントを起動しました。少々お待ちください。")

def invoke_hsq_translation_api(
    access_token: str,
    audio_file_box_id: str,
    audio_file_name: str,
    input_container_sas_url: str,
    output_container_sas_url: str,
    slack_channel_id: str,
    slack_channel_member: str,
    option: str = ""
):
    """
    HULFT Squareの音声ファイル変換API（pmassistantエンドポイント）にリクエストを送信し、
    音声ファイル情報・SAS URL・Slackチャンネル情報などを指定してAPIを呼び出します。
    レスポンスとしてJSONを返します。
    例外発生時には不足しているパラメータをログに出力します。

    Args:
        access_token (str): Bearerトークン
        audio_file_box_id (str): BoxのファイルID
        audio_file_name (str): 音声ファイル名
        input_container_sas_url (str): 入力先コンテナのSAS URL
        output_container_sas_url (str): 出力先コンテナのSAS URL
        slack_channel_id (str): SlackチャンネルID
        slack_channel_member (str): Slackチャンネルメンバー（例: '@junichi_kudo @shingo_kawahara @naoto_minagawa'）
        option (str): 個別指定のPJ分析アウトライン（任意）

    Returns:
        dict: APIレスポンスのJSON
    """
    import requests

    url = "https://a00001-21.square.hulft.com/PMAssistant/pmassistant"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {access_token}"
    }
    body = {
        "audioFileBoxId": audio_file_box_id,
        "audioFileName": audio_file_name,
        "inputContainerSasUrl": input_container_sas_url,
        "outputContainerSasUrl": output_container_sas_url,
        "slackChannelId": slack_channel_id,
        "slackChannelMember": slack_channel_member,
        "option": option
    }

    try:
        response = requests.post(url, json=body, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        # パラメータの存在を確認
        import logging
        missing_params = []
        if not access_token:
            missing_params.append("access_token")
        if not audio_file_box_id:
            missing_params.append("audio_file_box_id")
        if not audio_file_name:
            missing_params.append("audio_file_name")
        if not input_container_sas_url:
            missing_params.append("input_container_sas_url")
        if not output_container_sas_url:
            missing_params.append("output_container_sas_url")
        if not slack_channel_id:
            missing_params.append("slack_channel_id")
        if not slack_channel_member:
            missing_params.append("slack_channel_member")
        if missing_params:
            logging.error("以下のパラメータが不足しています: %s", ', '.join(missing_params))
        raise e

def ex_get_container_sas_url(container_name: str):
    """
    Azure Storageの指定されたコンテナのSAS URLを取得します。
    発行URLに対して"&restype=container&comp=list"を付記するとLIST形式で参照可能です。
    """

    # 存在チェック
    if container_name is None:
        raise ValueError("container_name is required")
        
    # 環境変数から値を取得
    account_name = os.environ.get("AZURE_STORAGE_ACCOUNT_NAME")
    account_key = os.environ.get("AZURE_STORAGE_ACCOUNT_KEY")
    
    # 環境変数の存在チェック
    if not account_name:
        raise ValueError("AZURE_STORAGE_ACCOUNT_NAME environment variable is not set")
    if not account_key:
        raise ValueError("AZURE_STORAGE_ACCOUNT_KEY environment variable is not set")
    
    print(f"アカウント名: {account_name}, コンテナ名: {container_name}")
    
    return get_container_sas_url(
        account_name=account_name,
        account_key=account_key,
        container_name=container_name
    )

# イベントハンドラ
@app.command("/pmassistant_form_open")
def post_pm_assistant_form_open_button_message(ack, say) -> None:
    """
    /pmassistant_form コマンドが実行された場合、フォームを開くボタンを含んだメッセージを送信します。
    member_joined_channel イベントで実行しようとしていましたが、イベントが発火せず、原因不明のためコマンドにしています。
    """
    ack()

    say(
        {
            "text": "PMアシスタント用メッセージ",
            "blocks": pm_assistant_form_open_button_block(),
        }
    )


@app.action("pma-form-open-submit-button")
def handle_pma_form_open(ack, body, client, logger: Logger) -> None:
    """
    Slackチャンネル上でPMアシスタントAIボタンが押された場合、入力フォームを開きます。
    """
    ack()

    slack_user = body["user"]
    slack_user_name = slack_user["name"]

    # システムユーザーID（メンバーから除外）
    system_user_id = "U0943JQLEER"

    # SAS URL取得
    audio_container_sas_url = ex_get_container_sas_url("audio")
    transcriptions_container_sas_url = ex_get_container_sas_url("transcriptions")
    print(f"audio_container_sas_url: {audio_container_sas_url}")
    print(f"transcriptions_container_sas_url: {transcriptions_container_sas_url}")

    try:
        # チャンネルIDを取得
        channel_id = body.get("channel", {}).get("id")
        member_ids = []
        if channel_id:
            try:
                # チャンネルメンバーの取得
                members_info = client.conversations_members(channel=channel_id)

                print(f"members_info: {members_info}")

                member_ids = members_info.get("members", [])
                # システムユーザー名を除外
                member_ids = [member_id for member_id in member_ids if member_id != system_user_id]
            except Exception as e:
                logger.warning("チャンネルメンバー取得時に例外が発生しました: %s", e)
        else:
            logger.info("チャンネルIDが取得できませんでした。")

        # hidden値をjsonにまとめて次の画面に渡す
        hidden_values = {
            "audio_container_sas_url": audio_container_sas_url,
            "transcriptions_container_sas_url": transcriptions_container_sas_url,
            "channel_id": channel_id
        }
        # pm_assistant_form_blockにメンバーIDリストを渡す
        # trigger_idは一度だけ使用可能
        client.views_open(
            trigger_id=body["trigger_id"],
            view=pm_assistant_form_block(slack_user["id"], member_ids, hidden_values),
        )
        logger.info("%s によってPMアシスタント投稿フォームが開かれました。", slack_user_name)

        # チャンネル情報とメンバー情報をログ出力（任意で残す場合）
        if channel_id:
            try:
                # チャンネル情報の取得
                try:
                    channel_info = client.conversations_info(channel=channel_id)
                    channel_name = channel_info["channel"].get("name")
                    logger.info("チャンネルID: %s, チャンネル名: %s", channel_id, channel_name)
                except Exception as e:
                    logger.warning("チャンネル情報取得時に例外が発生しました: %s", e)

                # メンバーの表示名もログ出力
                member_details = []
                for member_id in member_ids:
                    try:
                        user_info = client.users_info(user=member_id)
                        display_name = user_info["user"]["profile"].get("display_name") or user_info["user"]["name"]
                        member_details.append(f"{member_id} ({display_name})")
                    except Exception as e:
                        member_details.append(f"{member_id} (名前取得失敗)")
                        logger.warning("ユーザー情報取得時に例外が発生しました: %s", e)
                logger.info("チャンネル参加メンバー一覧: %s", member_details)

            except Exception as e:
                logger.exception("チャンネル情報またはメンバー取得時に予期せぬ例外が発生しました: %s", e)

    except Exception:
        logger.exception(
            "%s によるPMアシスタント投稿フォーム呼び出し時に例外が発生しました。",
            slack_user_name
        )
        

@app.view("pm_assistant_form")
def handle_pm_assistant_form_post(ack, body, view: dict, client, logger: Logger):
    """
    Slack上の入力フォーム上で"チェック"が選択された場合、入力情報をパラメータとしてHULFTSquareのジョブ起動エンドポイントにリクエストを発行します。
    """
    ack()

    logger.info("PMアシスタントAI機能を実行中です:hourglass_flowing_sand:\nしばらくお待ちください…")

    
    slack_user = body["user"]
    
    
    # 各変数を定義
    view_state = view["state"]["values"]
    # プロジェクトメンバー（ユーザーIDリスト）
    member_ids = view_state["member_name"][list(view_state["member_name"].keys())[0]]["selected_users"]
    # MTGアウトライン（テキスト）
    agenda_text = view_state["agenda"][list(view_state["agenda"].keys())[0]]["value"]
    # Boxファイルパス（テキスト）
    box_file_path = view_state["box_url"][list(view_state["box_url"].keys())[0]]["value"]
    # private_metadataのパース
    
    # "https://sisco001.ent.box.com/file/1860511521190?s=acq6wu4mwew7wedsilyb93r41fbvopmk"のs=以降の文字列を取得
    box_file_id = box_file_path.split("s=")[-1]

    audio_file_name = "test" # おそらく取得できないので仮で

    private_metadata = json.loads(view.get("private_metadata", "{}"))
    audio_container_sas_url = private_metadata.get("audio_container_sas_url")
    transcriptions_container_sas_url = private_metadata.get("transcriptions_container_sas_url")
    channel_id_from_metadata = private_metadata.get("channel_id")


    # def find_by_block_id(block_id: str) -> dict:
    #     """Block IDから入力された値を取得します。"""
    #     return list(view["state"]["values"][block_id].values())[0]

    try:

        #1.slackにメッセージ送信
        post_user_id = body["user"]["id"]
        #post_user_profile = _get_user_profile_by_slack_user_id(client, post_user_id)
        client.chat_postMessage(
            channel=channel_id_from_metadata,
            text="PMアシスタントAI機能を実行中です:hourglass_flowing_sand:\nしばらくお待ちください…"        
            )

        
        #2 HSQトークン取得
        access_token, challenge = get_access_token()
        new_access_token = update_refresh_token(access_token)

        # print(f"access_token: {access_token}")
        # print(f"new_access_token: {new_access_token}")

        # print(f"box_file_id: {box_file_id}")
        # print(f"audio_file_name: {audio_file_name}")
        # print(f"audio_container_sas_url: {audio_container_sas_url}")
        # print(f"transcriptions_container_sas_url: {transcriptions_container_sas_url}")
        # print(f"channel_id_from_metadata: {channel_id_from_metadata}")
        # print(f"member_ids: {member_ids}")
        # print(f"agenda_text: {agenda_text}")

        # tokenは取得成否として、その他のパラメータはjsonにセットしてlog出力
        log_body = {
            "access_token": access_token,
            "new_access_token": new_access_token,
            "box_file_id": box_file_id,
            "audio_file_name": audio_file_name,
            "audio_container_sas_url": audio_container_sas_url,
            "transcriptions_container_sas_url": transcriptions_container_sas_url,
            "channel_id_from_metadata": channel_id_from_metadata,
            "member_ids": member_ids,
            "agenda_text": agenda_text
        }
        logger.info(f"log_body: {log_body}")

        # #3.HULFT Squareのジョブを叩く
        # res = invoke_hsq_translation_api(
        #     access_token=access_token,
        #     audio_file_box_id=box_file_id,
        #     audio_file_name=audio_file_name,
        #     input_container_sas_url=audio_container_sas_url,
        #     output_container_sas_url=transcriptions_container_sas_url,
        #     slack_channel_id=channel_id_from_metadata,
        #     slack_channel_member=member_ids,
        #     option=agenda_text
        # )

        logger.info("PMアシスタントAI機能が終了しました。")
    except:
        logger.exception("PMアシスタントAI機能実行時に例外が発生しました。")

# Socket Modeハンドラーを実行する関数
def run_socket_mode():
    handler = SocketModeHandler(
        app=app,
        app_token=app_token,
        trace_enabled=True,
        auto_reconnect_enabled=True
    )
    handler.start()

if __name__ == "__main__":
    # 環境変数に基づいて実行モードを切り替え
    # AZURE_WEBAPP_MODE が設定されている場合はハイブリッドモード、それ以外は従来のSocket Modeのみ
    is_azure_webapp = os.environ.get("AZURE_WEBAPP_MODE", "").lower() == "true"
    
    if is_azure_webapp:
        logger.info("Azure Web App モードで起動しています")
        # Socket Modeを別スレッドで実行
        socket_thread = Thread(target=run_socket_mode)
        socket_thread.daemon = True
        socket_thread.start()
        
        # Flaskサーバーを起動（Azure App Serviceが期待するポート8000で）
        port = int(os.environ.get("PORT", 8000))
        flask_app.run(host="0.0.0.0", port=port)
    else:
        logger.info("ローカルモードで起動しています。")
        # 従来通りSocket Modeのみで実行
        run_socket_mode()